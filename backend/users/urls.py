from django.urls import path, include
from rest_framework import routers

from .views import UserViewSet, GetTokenView, DeleteTokenView

auth_patern = [
    path('login/', GetTokenView.as_view()),
    path('logout/', DeleteTokenView.as_view()),
]
router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', include(auth_patern))
]
