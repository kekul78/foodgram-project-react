from django.db import models
from django.contrib.auth.models import AbstractUser

import foodgram_backend.constants as const
from .validators import validate_forbidden_username


class MyUserModel(AbstractUser):
    email = models.EmailField(
        verbose_name='E-mail',
        unique=True,
        max_length=const.MAX_EMAIL_LENGTH,
        help_text='Введите адрес эллектронной почты'
    )
    username = models.CharField(
        verbose_name='Логин',
        unique=True,
        max_length=const.MAX_LENGTH,
        help_text='Введите логин',
        validators=[validate_forbidden_username]
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=const.MAX_LENGTH,
        help_text='Введите имя',
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=const.MAX_LENGTH,
        help_text='Введите фамилию',
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=const.MAX_LENGTH,
        help_text='Введите пароль',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    author = models.ForeignKey(
        MyUserModel,
        verbose_name='Автор',
        related_name='subscribe',
        on_delete=models.CASCADE,
    )
    subscriber = models.ForeignKey(
        MyUserModel,
        verbose_name='Подписчик',
        related_name='folower',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ('author',)
        constraints = [
            models.UniqueConstraint(fields=['author', 'subscriber'],
                                    name='unique_suscribe')
        ]
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.subscriber} {self.author}'
