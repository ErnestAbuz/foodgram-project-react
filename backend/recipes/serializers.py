from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from users.serializers import UserAuthSerializer

from .models import Ingredient, IngredientRecipe, Recipe, Tag
from .validators import validate_zero


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = '__all__',


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(
        write_only=True, validators=[validate_zero]
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('slug', 'color')


class RecipeWriteSerializer(serializers.ModelSerializer):
    author = UserAuthSerializer(
        default=serializers.CurrentUserDefault(), read_only=True
    )
    ingredients = IngredientRecipeSerializer(
        many=True
    )
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta:
        exclude = ('favorites', 'shopping_cart')
        model = Recipe

    def add_ingredients(self, recipe, ingredients):
        for ingridient in ingredients:
            IngredientRecipe.objects.create(
                ingredient_id=ingridient.get('id'),
                amount=ingridient.get('amount'),
                recipe=recipe
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.add_ingredients(recipe, ingredients)
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        super().update(instance, validated_data)
        instance.ingredients.clear()
        instance.tags.set(tags)
        self.add_ingredients(instance, ingredients)
        instance.save()
        return instance


class RecipeReadSerializer(RecipeWriteSerializer):
    author = UserAuthSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    tags = TagSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('ingredient_recipe__amount')
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.favorites.filter(pk=obj.pk).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.shopping_cart.filter(pk=obj.pk).exists()
        return False
