from django.urls import path, include
from rest_framework import routers

from .views import TagViewSet, IngredientViewSet, RecipeView

router = routers.DefaultRouter()
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeView, basename='recipes')

urlpatterns = [
    path('', include(router.urls))
]
