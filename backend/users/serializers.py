import datetime
import re

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from djoser.serializers import (UserSerializer,
                                UserCreateSerializer)

from .models import CustomUser

# from events.serializers import EventGetSerializer


class RegisterUserSerializer(UserCreateSerializer):
    """Кастомный базовый сериализатор регистрации пользователя."""

    class Meta:
        model = CustomUser
        fields = ('id',
                  'username',
                  'email',
                  'first_name',
                  'last_name',
                  'phone_number',
                  'photo',
                  'birth_year',
                  'bio',
                  'password')

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
    
    def validate_birth_year(self, value):
        if value >= datetime.datetime.now().year:
            raise ValidationError('Некорректный формат данных')
        return value


class CustomUserSerializer(UserSerializer):
    """Кастомный сериализатор пользователей."""
    age = serializers.SerializerMethodField()
    subscribers_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    # event_author = EventGetSerializer(many=True, read_only=True)
    # participation = EventGetSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id',
                  'username',
                  'email',
                  'first_name',
                  'last_name',
                  'phone_number',
                  'photo',
                  'age',
                  'bio',
                  'is_subscribed',
                  'subscribers_count',
                #   'event_author',
                #   'participation'
                  )

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
