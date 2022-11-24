from re import fullmatch

from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from djoser.serializers import UserSerializer
from recipes.models import Recipe
from rest_framework import serializers
from users.models import Subscription, User


class CustomUserSerializer(UserSerializer):
    """Класс регистрации пользователей"""
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create(
            password=make_password(validated_data['password']),
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.save()
        return user

    def validate_username(self, value):
        if value.lower() == 'me':
            raise ValidationError('Нельзя создать пользователя с именем me')
        if not fullmatch(r'[a-zA-Z0-9.@+-]{1,150}', value):
            raise ValidationError('Имя пользователя может содержать только '
                                  'латинские буквы, цифры и символы: @.+-')
        return value


class UserActionGetSerializer(UserSerializer):
    """Класс получения данных пользователей"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, value):
        user = self.context['request'].user
        if user.is_authenticated:
            subscription = Subscription.objects.filter(author=value, user=user)
            return subscription.exists()
        return False  # Если пользователь аноним


class RecipePartInfoSerializer(serializers.ModelSerializer):
    """Класс рецептов с минимальным количеством информации."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(UserActionGetSerializer):
    """Класс получения данных подписок на авторов."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        limit = self.context['request'].query_params.get('recipes_limit')
        if limit is None:
            recipes = obj.recipes.all()
        else:
            recipes = obj.recipes.all()[:int(limit)]
        return RecipePartInfoSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
