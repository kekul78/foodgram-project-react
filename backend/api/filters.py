import django_filters
from rest_framework.filters import SearchFilter

from recipes.models import Ingredient, Recipe, Tag


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug')
    is_favorited = django_filters.filters.NumberFilter(
        method='is_recipe_in_favorites_filter')
    is_in_shopping_cart = django_filters.filters.NumberFilter(
        method='is_recipe_in_shoppingcart_filter')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def is_recipe_in_favorites_filter(self, queryset, name, value):
        if value == 1:
            user = self.request.user
            return queryset.filter(favorites__user_id=user.id)
        return queryset

    def is_recipe_in_shoppingcart_filter(self, queryset, name, value):
        if value == 1:
            user = self.request.user
            return queryset.filter(shopping_recipe__user_id=user.id)
        return queryset
