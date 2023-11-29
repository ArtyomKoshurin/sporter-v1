from rest_framework import serializers

from .models import (
    Activity,
    EventPost,
    Participation,
    Comment,
    Like
)

from users.models import CustomUser

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
    participants = serializers.PrimaryKeyRelatedField(
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

    def validate_activity(self, values_list):
        for elem_id in values_list:
            if not Activity.objects.filter(id=elem_id).exists():
                raise serializers.ValidationError(
                    {'Ошибка': 'Такого вида активности не существует.'}
                )
        return values_list

    def create(self, validated_data):
        activity_list = validated_data.pop('activity')
        event = EventPost.objects.create(**validated_data)

        event.activity.set(activity_list)
        # event.save()

        return event

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.duration = validated_data.get('duration', instance.duration)
        instance.datetime = validated_data.get('datetime', instance.datetime)
        instance.location = validated_data.get('location', instance.place)
        activity = validated_data.pop('activity')
        instance.activity.clear()
        activity_name = Activity.objects.get_or_create(
            name=activity.get('name')
        )
        instance.activity = activity_name
        instance.save()

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
