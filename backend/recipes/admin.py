from django.contrib import admin

from .models import Tag, Ingredient, Recipe, RecipeIngredient


class RecepIngredientsInLine(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Tag)
class BlogAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe, Ingredient)
class RecepiesAdmin(admin.ModelAdmin):
    inlines = (RecepIngredientsInLine,)
