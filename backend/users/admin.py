from django.contrib import admin

from .models import MyUserModel, Subscribe


@admin.register(MyUserModel, Subscribe)
class BlogAdmin(admin.ModelAdmin):
    pass
