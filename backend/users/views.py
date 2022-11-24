from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from api.pagination import ForPageNumberPagination
from users.models import Subscription, User
from users.serializers import (CustomUserSerializer, SubscriptionSerializer,
                               SubscriptionShowSerializer,
                               UserActionGetSerializer)


class CustomUserViewSet(UserViewSet):
    """Класс регистрации и работы с пользователями и подписками на авторов"""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (AllowAny,)
    pagination_class = ForPageNumberPagination

    @action(detail=False, url_path='me', permission_classes=[IsAuthenticated])
    def me(self, request):
        context = {'request': self.request}
        serializer = UserActionGetSerializer(request.user, context=context)
        return Response(serializer.data)

    @action(detail=False, url_path='subscriptions',
            methods=['get'], permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        authors = User.objects.filter(author__user=request.user)
        result_pages = self.paginate_queryset(
            queryset=authors, request=request
        )
        serializer = SubscriptionShowSerializer(
            result_pages, context={'request': request}, many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'], detail=False,
            url_path='subscribe',
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                data={'follower': request.user.id, 'author': author.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            author_serializer = SubscriptionShowSerializer(
                author, context={'request': request}
            )
            return Response(
                author_serializer.data, status=status.HTTP_201_CREATED
            )
        subscription = get_object_or_404(
            Subscription, subscriber=request.user, author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
