from django.conf import settings
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientRecipe,
                            IngredientsAmount, Recipe, ShoppingCart, Tag)
from rest_framework import serializers
from users.serializers import UserActionGetSerializer


class IngredientSerializer(serializers.ModelSerializer):
    """Класс ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientsAmountSerializer(serializers.ModelSerializer):
    """Класс количества ингредиентов."""
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = IngredientsAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_name(self, value):
        name = value.ingredient.name
        return name

    def get_measurement_unit(self, value):
        measurement_unit = value.ingredient.measurement_unit
        return measurement_unit


class TagSerializer(serializers.ModelSerializer):
    """Класс тэгов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    """Класс рецептов."""
    author = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    ingredients = IngredientsAmountSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_author(self, value):
        request = self.context['request']
        author = value.author
        context = {'request': request}
        serializer = UserActionGetSerializer(author, context=context)
        return serializer.data

    def favorited_or_in_shopping_cart(self, value, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            object = obj.objects.filter(recipe=value, user=user)
            return object.exists()
        return False

    def get_is_favorited(self, value):
        return self.favorited_or_in_shopping_cart(value, obj=Favorite)

    def get_is_in_shopping_cart(self, value):
        return self.favorited_or_in_shopping_cart(value, obj=ShoppingCart)


class AddIngredientSerializer(serializers.ModelSerializer):
    """Вспомогательный сериализатор для RecipeCreateSerializer."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Класс создания рецептов."""
    author = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    image = Base64ImageField()
    ingredients = serializers.ListField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'tags', 'image', 'name',
                  'text', 'cooking_time',)

    def validate(self, data):
        tags = data['tags']
        if not tags:
            raise serializers.ValidationError({
                'tags': 'Тег обязателен для заполнения!'
            })
        tags_set = set()
        for tag in tags:
            if tag in tags_set:
                raise serializers.ValidationError({
                    'tags': f'Тег {tag} существует, измените тег!'
                })
            tags_set.add(tag)
        ingredients = data['ingredients']
        ingredients_set = set()
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Ингредиенты обязателены для заполнения!'
            })
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_set:
                raise serializers.ValidationError({
                    'ingredients': f'Ингредиент {ingredient} существует,'
                                   ' измените ингредиент!'
                })
            ingredients_set.add(ingredient_id)
            amount = ingredient['amount']
            if int(amount) < settings.MIN_INGREDIENTS_AMOUNT:
                raise serializers.ValidationError({
                    'amount': 'Количество должно быть больше 0!'
                })
        cooking_time = data['cooking_time']
        if int(cooking_time) < settings.MIN_COOKING_TIME:
            raise serializers.ValidationError({
                'cooking_time': 'Время приготовления должно быть больше 0!'
            })
        return data

    def add_ingredients(self, ingredients, recipe):
        new_ingredients = [IngredientsAmount(
            recipe=recipe,
            ingredient=ingredient['id'],
            amount=ingredient['amount'],
        ) for ingredient in ingredients]
        IngredientsAmount.objects.bulk_create(new_ingredients)

    def add_tags(self, tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.add_tags(tags, recipe)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def update(self, recipe, validated_data):
        recipe.tags.clear()
        IngredientsAmount.objects.filter(recipe=recipe).delete()
        self.add_tags(validated_data.pop('tags'), recipe)
        self.add_ingredients(validated_data.pop('ingredients'), recipe)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(instance, context=context).data
