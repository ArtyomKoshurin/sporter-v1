from django.db import transaction
from django.conf import settings

from geopy import Yandex

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import (Activity,
                     Event,
                     Comment,
                     Location,
                     Participation)

from users.serializers import CustomUserContextSerializer


class ActivitySerializer(serializers.ModelSerializer):
    """Сериализатор для видов спорта."""
    class Meta:
        model = Activity
        fields = ('id', 'name')


class LocationSerializer(serializers.ModelSerializer):
    """Сериализатор для локации."""
    address = serializers.CharField(required=False)
    point = serializers.CharField(required=False)

    class Meta:
        model = Location
        fields = ('id', 'address', 'point')


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для создания комментария к посту."""
    author = CustomUserContextSerializer(
        default=serializers.CurrentUserDefault()
    )
    pub_date = serializers.DateTimeField(read_only=True, format='%d.%m.%Y')
    event = serializers.PrimaryKeyRelatedField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id',
                  'author',
                  'text',
                  'pub_date',
                  'event',
                  'is_liked',
                  'likes_count')

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        instance.save()

        return instance

    def get_is_liked(self, comment):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return comment.users_for_liked_comment.filter(user=user).exists()

    def get_likes_count(self, comment):
        return comment.users_for_liked_comment.all().count()


class EventSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления постов о мероприятиях."""
    name = serializers.CharField(required=True)
    activity = serializers.PrimaryKeyRelatedField(
        queryset=Activity.objects.all(), many=True
    )
    datetime = serializers.DateTimeField(format='%d.%m.%Y')
    author = CustomUserContextSerializer(
        default=serializers.CurrentUserDefault()
    )
    duration = serializers.IntegerField(required=True)
    location = LocationSerializer()
    is_favorite = serializers.SerializerMethodField()
    is_participate = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    participants_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ('id',
                  'name',
                  'description',
                  'activity',
                  'datetime',
                  'author',
                  'duration',
                  'location',
                  'comments',
                  'is_favorite',
                  'is_participate',
                  'participants_count')
        
        validators = [
            UniqueTogetherValidator(queryset=Event.objects.all(),
                                    fields=['name', 'author', 'datetime'])
        ]
        
    def get_location(self, location):
        if location.get('address'):
            location_data = Yandex(
                api_key=settings.API_KEY
            ).geocode(location['address'])
            location['address'] = location_data.address
            location['point'] = f'POINT({location_data.longitude} {location_data.latitude})'

        elif location.get('point'):
            point = location.get('point')
            location_data = Yandex(
                api_key=settings.API_KEY
            ).reverse(point)

            location['address'] = location_data.address
            location['point'] = f'POINT({point})'

        return location


    def validate_name(self, value):
        if len(value) > 124:
            raise serializers.ValidationError(
                'Название мероприятия не должно превышать 124 символов.'
            )
        return value

    def validate_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Введите корректную длительность мероприятия.'
            )
        return value

    def validate(self, data):
        activities_list = self.initial_data.get('activity')
        if activities_list:
            for elem_id in activities_list:
                if not Activity.objects.filter(id=elem_id).exists():
                    raise serializers.ValidationError(
                        'Такого вида активности не существует.'
                    )
        else:
            raise serializers.ValidationError(
                'Необходимо указать минимум один вид активности!'
            )

        return data

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        activity_list = validated_data.pop('activity')
        location = validated_data.pop('location')
        location = self.get_location(location)
        location = Location.objects.create(**location)

        event = Event.objects.create(location=location, **validated_data)
        event.activity.set(activity_list)

        Participation.objects.create(event=event, user=user)
        return event

    @transaction.atomic
    def update(self, instance, validated_data):
        activity_list = validated_data.pop('activity', instance.activity)
        instance = super().update(instance, validated_data)
        instance.save()
        instance.activity.clear()
        instance.activity.set(activity_list)
        return instance

    def get_is_favorite(self, event):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.favorite_for_user.filter(event=event).exists()

    def get_is_participate(self, event):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.events_participation_for_user.filter(event=event).exists()

    def get_participants_count(self, event):
        return event.users_participation_for_event.all().count()

    def get_comments(self, event):
        request = self.context.get('request')
        event = event.comments.all().order_by('-id')[:3]
        serializer = CommentSerializer(
            event,
            context={'request': request},
            many=True
        )
        return serializer.data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['activity'] = instance.activity.values()
        # data['location'] = instance.location.address
        return data
