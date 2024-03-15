from rest_framework import serializers
from djoser.serializers import UserCreateSerializer

from .models import MyUserModel, Subscribe


class UserGetSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'id')
        model = MyUserModel


class CustomUserSerializer(UserCreateSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = MyUserModel
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        subscriber = self.context.get('request').user
        if subscriber.is_anonymous:
            return False
        return Subscribe.objects.filter(subscriber=subscriber,
                                        author=obj.id).exists()


class CustomCreateUserSerializer(CustomUserSerializer):

    class Meta:
        model = MyUserModel
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}
