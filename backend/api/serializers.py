from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientsAmount, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from users.serializers import UserActionGetSerializer


class IngredientSerializer(serializers.ModelSerializer):
    """Класс ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientsAmountSerializer(serializers.ModelSerializer):
    """Класс количества ингредиентов."""
    id = serializers.ReadOnlyField(source='ingredient.id')
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

    def validate_ingredients(self, value):
        validated_ingredients = []
        for ingredient_value in value:
            min_amount = settings.MIN_INGREDIENTS_AMOUNT
            if int(ingredient_value['amount']) < min_amount:
                raise serializers.ValidationError(
                    'Количество ингредиентов должно быть больше 0'
                )
            ingredient_id = ingredient_value['id']
            ingredient = get_object_or_404(Ingredient, id=ingredient_id)
            ingredients_amount = IngredientsAmount.objects.get(
                ingredient=ingredient,
                amount=ingredient_value['amount'],
            )
            validated_ingredients.append(ingredients_amount[0].id)
        return validated_ingredients

    def validate_tags(self, value):
        validated_tags = []
        for tags_value in value:
            min_amount = settings.MIN_TAGS_AMOUNT
            if value > min_amount:
                tags_id = tags_value['id']
                name = get_object_or_404(Tag, id=tags_id)
                tags_check = Tag.objects.get(
                    name=name,
                    slug=tags_value['slug']
                )
                validated_tags.append(tags_check[0].id)
                return validated_tags
            raise serializers.ValidationError(
                'Количество тэгов должно быть больше 0'
            )

    def validate_cooking_time(self, value):
        if value >= settings.MIN_COOKING_TIME:
            return value
        raise serializers.ValidationError('Время готовки должно быть больше 0')

    def add_ingredients(self, ingredients):
        new_ingredients = [IngredientsAmount(
            ingredient=ingredient['id'],
            amount=ingredient['amount'],
        ) for ingredient in ingredients]
        IngredientsAmount.objects.bulk_create(new_ingredients)

    def add_tags(self, tags):
        for tag in tags:
            tags.add(tag)

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
