from django.contrib import admin
from django.contrib.admin import register, ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

from .models import MyUserModel, Subscribe


@register(MyUserModel)
class MyUserAdmin(UserAdmin):
    list_display = ('pk', 'username', 'email', 'first_name', 'last_name',
                    'password')
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')


@register(Subscribe)
class SubscribeAdmin(ModelAdmin):
    list_display = ('pk', 'subscriber', 'author')
    search_fields = ('subscriber', 'author')
    list_filter = ('subscriber', 'author')


admin.site.unregister(TokenProxy)

admin.site.unregister(Group)
