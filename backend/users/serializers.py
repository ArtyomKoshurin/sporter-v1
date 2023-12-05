import datetime
import re
import base64

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.core.files.base import ContentFile

from djoser.serializers import (UserSerializer,
                                UserCreateSerializer)

from .models import CustomUser
from events.models import Activity


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


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
    birth_year = serializers.IntegerField(write_only=True)
    photo = Base64ImageField()
    activity = serializers.PrimaryKeyRelatedField(
        queryset=Activity.objects.all(), many=True
    )

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
                  'birth_year',
                  'activity'
                  )

    def validate_birth_year(self, value):
        if (datetime.datetime.now().year - value) > 120:
            raise serializers.ValidationError(
                'Проверьте возраст.'
            )
        return value

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

    def update(self, instance, validated_data):
        activity = validated_data.pop('activity')
        instance.birth_year = validated_data.get(
            'birth_year', instance.birth_year
        )
        instance.bio = validated_data.get('bio', instance.bio)
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get(
            'first_name', instance.first_name
        )
        instance.last_name = validated_data.get(
            'last_name', instance.last_name
        )
        instance.phone_number = validated_data.get(
            'phone_number', instance.phone_number
        )
        instance.activity.clear()
        instance.activity.set(activity)
        instance.save()

        return instance
