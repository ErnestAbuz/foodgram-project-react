from djoser.serializers import UserCreateSerializer
from recipes.models import Recipe
from rest_framework import serializers

from .models import User


class RecipeForUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class UserAuthSerializer(UserCreateSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta(UserCreateSerializer.Meta):
        fields = (
            'username', 'id', 'email', 'first_name', 'last_name', 'password',
            'is_subscribed',
        )
        extra_kwargs = {'password': {'write_only': True}}
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.followers.filter(pk=obj.pk).exists()
        return False


class UserSerializer(UserAuthSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )
        model = User

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj)
        return RecipeForUserSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
