from django.urls import path, include
from rest_framework import routers

from .views import CustomUserViewSet

router = routers.DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('users/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
