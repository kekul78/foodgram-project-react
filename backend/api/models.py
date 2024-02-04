from django.db import models


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        unique=True,
        blank=False
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=7,
        unique=True,
        blank=False
        )
    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=200,
        unique=True,
        blank=False,
        db_index=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ("name",)


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        blank=False,
        unique=True,
        db_index=True
    )
    measurement_unit = models.CharField(
        verbose_name='Еденица измерения',
        max_length=200,
        blank=False
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ("name",)
