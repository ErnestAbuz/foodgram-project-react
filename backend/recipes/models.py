from django.core import validators
from django.db import models
from users.models import User

from .validators import validate_zero


class Ingredient(models.Model):
    name = models.CharField(
        max_length=100, verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(max_length=20)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField('Название тега', max_length=50, unique=True)
    color = models.CharField(
        'HEX-код цвета',
        max_length=7,
        unique=True,
        validators=[
            validators.RegexValidator(
                regex=r'^#[a-fA-F\d]{6}$',
                message='Неверное значение HEX-кода'
            )
        ],
    )
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    name = models.CharField('Название рецепта', max_length=200)
    image = models.ImageField(
        'Фото блюда',
        upload_to='recipes/',
        help_text='Добавьте картинку',
    )
    text = models.TextField(
        'Описание рецепта',
        help_text='Введите описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='ingredients',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='tags',
        verbose_name='Тэги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах',
        help_text='Время в минутах',
        validators=[validate_zero],
    )
    favorites = models.ManyToManyField(
        User,
        related_name='favorites',
        verbose_name='Избранное',
        blank=True
    )
    shopping_cart = models.ManyToManyField(
        User,
        related_name='shopping_cart',
        verbose_name='Список покупок',
        blank=True
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
        verbose_name='Название ингредиента'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredient_recipe'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[validate_zero],
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
    
    def __str__(self):
        return (
            f'{self.ingredient.name}'
            f'({self.ingredient.measurement_unit})'
            f' - {self.amount}'
        )
