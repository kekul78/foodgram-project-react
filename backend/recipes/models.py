from django.db import models
from django.core.validators import MinValueValidator
from colorfield.fields import ColorField

import foodgram_backend.constants as const
from users.models import MyUserModel


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=const.BIG_MAX_LENGTH,
        unique=True,
    )
    color = ColorField(
        verbose_name='Цвет',
        max_length=const.MAX_COLOR_LENGTH,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=const.BIG_MAX_LENGTH,
        unique=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        ordering = ("name",)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=const.BIG_MAX_LENGTH,
    )
    measurement_unit = models.CharField(
        verbose_name='Еденица измерения',
        max_length=const.BIG_MAX_LENGTH,
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'], name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        MyUserModel,
        related_name='recipes',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=const.BIG_MAX_LENGTH,
        unique=True,
        db_index=True
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None,
        blank=True
    )
    text = models.TextField(
        verbose_name='Описание',
        null=True,
        blank=True
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиент',
        related_name='recipes',
        through='recipeingredient',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(1)],
        error_messages={'validators': 'Время приготовления не '
                        'должно быть меньше 1 минуты'}
    )
    pub_date = models.DateTimeField(
        'Дата публикации рецепта',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ("name",)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_list',
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(1, message='Количество ингридиентов '
                                         'не должно быть меньше 1')
        ],
    )

    class Meta:
        verbose_name = 'ингридиент в рецепте'
        verbose_name_plural = 'Ингридиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredients'),
                name='unique_ingredients_in_the_recipe'
            )
        ]

    def __str__(self):
        return f'{self.ingredients}, кол-во: {self.amount}'


class AbstractModel(models.Model):

    user = models.ForeignKey(
        MyUserModel,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True


class Favorite(AbstractModel):

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]
        default_related_name = 'favorites'

    def __str__(self):
        return f'{self.user} {self.recipe}'


class ShoppingCart(AbstractModel):
    user = models.ForeignKey(
        MyUserModel,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        verbose_name='Пользователь'
    )

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shoppingcart'
            )
        ]
        default_related_name = 'shopping_recipe'

    def __str__(self):
        return f'{self.user} {self.recipe}'
