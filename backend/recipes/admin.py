from django.contrib import admin

from .models import (
    Tag,
    ShoppingCart,
    RecipeIngredient,
    Recipe,
    Ingredient,
    Favorite,
)


class RecepIngredientsInLine(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1
    extra = 1


@admin.register(Recipe)
class RecepiesAdmin(admin.ModelAdmin):
    inlines = (RecepIngredientsInLine,)
    list_display = (
        'pk', 'name', 'author', 'get_favorites', 'pub_date'
    )
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name',)

    def get_favorites(self, obj):
        return obj.favorites.count()

    get_favorites.short_description = (
        'Количество добавлений рецепта в избранное'
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    inlines = (RecepIngredientsInLine,)
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(RecipeIngredient)
class RecipeIngredient(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredients', 'amount')


@admin.register(Tag)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
