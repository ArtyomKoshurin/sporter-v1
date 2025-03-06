from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField

from events.models import Activity


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""
    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True
    )
    email = models.EmailField(
        _('email'),
        max_length=254,
        unique=True,
        null=False,
        blank=False
    )
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    phone_number = PhoneNumberField('Номер телефона', unique=True)
    photo = models.ImageField(
        'Фото профиля',
        upload_to='users/image/',
        null=True,
        blank=True
    )
    birth_year = models.IntegerField(
        'Год рождения',
        null=True,
        blank=True
    )
    bio = models.TextField(
        'О себе',
        null=True,
        blank=True
    )
    activities = models.ManyToManyField(
        Activity,
        through='FavoriteActivity',
        related_name='user_activities'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password']

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email', 'phone_number'],
                name='unique_user'
            ),
        ]


class Subscribe(models.Model):
    """Модель подписок."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    class Meta:
        ordering = ['author']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_subscribe')
        ]

    def __str__(self):
        return f'{self.user} {self.author}'
    

class FavoriteActivity(models.Model):
    """Вспомогательная модель любимых видов спорта пользователя."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='activities_for_user',
        on_delete=models.CASCADE
    )
    activity = models.ForeignKey(
        Activity,
        related_name='users_for_activity',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name_plural = 'Избранные активности пользователей'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'activity'],
                name='unique_activity_for_user'
            )
        ]

    def __str__(self):
        return f'{self.user}: {self.activity}'
