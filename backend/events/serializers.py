from django.db import transaction

from rest_framework import serializers

from .models import (
    Activity,
    EventPost,
    Comment
)

from users.serializers import CustomUserSerializer


class ActivitySerializer(serializers.ModelSerializer):
    """Сериализатор для видов спорта."""
    class Meta:
        model = Activity
        fields = ('id', 'name')


class EventSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления постов о мероприятиях."""
    name = serializers.CharField(required=True)
    activity = serializers.PrimaryKeyRelatedField(
        queryset=Activity.objects.all(), many=True
    )
    datetime = serializers.DateTimeField(format='%d.%m.%Y')
    author = CustomUserSerializer(
        default=serializers.CurrentUserDefault()
    )
    duration = serializers.IntegerField(required=True)
    is_participate = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    participants = CustomUserSerializer(
        read_only=True, many=True
    )

    class Meta:
        model = EventPost
        fields = ('id',
                  'name',
                  'description',
                  'activity',
                  'datetime',
                  'author',
                  'duration',
                  'location',
                  'is_participate',
                  'comments',
                  'participants')

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
        activity_list = validated_data.pop('activity')
        event = EventPost.objects.create(**validated_data)
        event.activity.set(activity_list)
        return event

    @transaction.atomic
    def update(self, instance, validated_data):
        activity_list = validated_data.pop('activity', instance.activity)

        instance = super().update(instance, validated_data)
        instance.save()
        instance.activity.clear()
        instance.activity.set(activity_list)

        return instance

    def get_is_participate(self, event):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.events_participation_for_user.filter(event=event).exists()

    def get_comments(self, event):
        return event.comments.all().order_by('-id')[:3]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['activity'] = instance.activity.values()
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для создания комментария к посту."""
    author = CustomUserSerializer(
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
