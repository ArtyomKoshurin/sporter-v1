import datetime
import re

# from django.shortcuts import get_object_or_404

# from drf_extra_fields.fields import Base64ImageField

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
# from rest_framework.validators import UniqueTogetherValidator

from djoser.serializers import (UserSerializer,
                                UserCreateSerializer)

from .models import CustomUser


class RegisterUserSerializer(UserCreateSerializer):
    """Кастомный базовый сериализатор регистрации пользователя."""

    class Meta:
        model = CustomUser
        fields = ('id',
                  'username',
                  'email',
                  'first_name',
                  'last_name',
                  'bio',
                  'birth_year',
                  'phone_number',
                  'password',
                  'photo',)

    def validate_username(self, data):
        username = data
        error_symbols_list = []

        for symbol in username:
            if not re.search(r'^[\w.@+-]+\Z', symbol):
                error_symbols_list.append(symbol)
        if error_symbols_list:
            raise serializers.ValidationError(
                f'Символы {"".join(error_symbols_list)} недопустимы'
            )
        return data


class CustomUserSerializer(UserSerializer):
    """Кастомный сериализатор пользователей."""
    age = serializers.SerializerMethodField()
    subscribers_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id',
                  'username',
                  'email',
                  'first_name',
                  'last_name',
                  'birth_year',
                  'phone_number',
                  'photo',
                  'age',
                  'bio',
                  'is_subscribed',
                  'subscribers_count')

    def get_age(self, user):
        if user.birth_year:
            return datetime.datetime.now().year - user.birth_year
        return
    
    def get_is_subscribed(self, author):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.subscriptions.filter(author=author).exists()
    
    def get_subscribers_count(self, user):
        return user.subscribers.all().count()
    
    # валидация не работает!
    def validate_age(self, value):
        if type(value) is not int or value >= datetime.datetime.now().year:
            raise ValidationError('Некорректный формат данных')
        return value
