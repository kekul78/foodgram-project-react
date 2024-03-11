from rest_framework import serializers

from .models import MyUserModel, Subscribe


class UserGetSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'id')
        model = MyUserModel


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = MyUserModel
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'is_subscribed': {'read_only': True}
        }

    def get_is_subscribed(self, obj):
        subscriber = self.context.get('request').user
        if subscriber.is_anonymous:
            return False
        return (
              Subscribe.objects.filter(subscriber=subscriber, author=obj.id)
              .exists()
        )


class UserTokenSerializer(serializers.Serializer):
    """Сериализатор запроса на получение кода подтверждения."""
    email = serializers.EmailField(max_length=254,
                                   required=True)
    password = serializers.CharField(max_length=150,
                                     required=True)

    def validate(self, data):
        """Проверка при введении правильного ника или почты."""
        if (MyUserModel.objects.filter(password=data['password']).exists()
                and not MyUserModel.objects
                .filter(email=data['email']).exists()):
            raise serializers.ValidationError(
                'Ошибка, проверьте правильность почты!')
        elif (not MyUserModel.objects
              .filter(password=data['password']).exists()
              and MyUserModel.objects.filter(email=data['email']).exists()):
            raise serializers.ValidationError(
                'Ошибка, проверьте правильность пароля!')
        return data


class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(max_length=150,
                                             required=True)
    new_password = serializers.CharField(max_length=150,
                                         required=True)

    def validate(self, data):
        user = self.instance
        current_password = data['current_password']
        if not MyUserModel.objects.filter(username=user,
                                          password=current_password).exists():
            raise serializers.ValidationError(
                'Ошибка, проверьте правильность пароля!')
        return data


class SubscribeSerializer(UserSerializer):

    class Meta:
        model = MyUserModel
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            "is_subscribed",
        )
