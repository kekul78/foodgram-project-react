from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.decorators import action
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import (
    Tag, Ingredient, Recipe, Favorite, ShoppingCart, RecipeIngredient
)
from .filters import IngredientSearchFilter, RecipeFilter
from .paginators import PagePagination
from .permissions import isAdminOrAuthorOrReadOnly
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeGetSerializer,
    FavoriteSerializer
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeView(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeGetSerializer
    pagination_class = PagePagination
    permission_classes = (isAdminOrAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeGetSerializer
        return RecipeCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    @action(methods=['post'], detail=True,
            permission_classes=(IsAuthenticated,),
            url_path='favorite', url_name='favorite')
    def favorite(self, request, pk):
        user = request.user
        if not Recipe.objects.filter(id=pk).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        recipe = Recipe.objects.get(id=pk)
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        Favorite.objects.create(user=user, recipe=recipe)
        serializer = FavoriteSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorite_chek = Favorite.objects.filter(user=user, recipe=recipe)
        if not favorite_chek.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        favorite_chek.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        user = request.user
        if not Recipe.objects.filter(id=pk).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        recipe = Recipe.objects.get(id=pk)
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ShoppingCart.objects.create(user=user, recipe=recipe)
        serializer = FavoriteSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        shop_cart_chek = ShoppingCart.objects.filter(user=user,
                                                     recipe=recipe)
        if not shop_cart_chek.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        shop_cart_chek.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('get',), detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_recipe__user=request.user
        ).values(
            'ingredients__name',
            'ingredients__measurement_unit'
        ).annotate(sum=Sum('amount'))
        shopping_list = ''
        for ingredient in ingredients:
            shopping_list += (
                f"{ingredient['ingredients__name']}  - "
                f"{ingredient['sum']}"
                f"({ingredient['ingredients__measurement_unit']})\n"
            )
        return HttpResponse(shopping_list, content_type='text/plain')
