from rest_framework import serializers

from .models import (
    Activity,
    ActivityForUser,
    EventPost,
    Participation,
    Comment,
)


class ActivitySerializer(serializers.ModelSerializer):
    """Сериализатор для видов спорта."""
    class Meta:
        model = Activity
        fields = ('id', 'name')


class EventPostGetSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра постов о мероприятиях."""
    activity = ActivitySerializer(read_only=True)
    author = CustomUserSerializer(read_only=True)
    is_participing = serializers.SerializerMethodField()

    class Meta:
        model = EventPost
        fields = ('name', 'text', 'activity', 'date', 'author', 'duration',
                  'place', 'is_participing')

    def get_is_participing(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False

        return Participation.objects.filter(
            post=obj, user=request.user).exists()


class EventPostCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления постов о мероприятиях."""
    name = serializers.CharField(required=True)
    text = serializers.CharField(required=True)
    activity = ActivitySerializer()
    date = serializers.DateTimeField(required=True)
    author = CustomUserSerializer(read_only=True)
    duration = serializers.IntegerField(required=True)
    place = serializers.CharField(required=True)

    class Meta:
        model = EventPost
        fields = ('name', 'text', 'activity', 'date', 'author', 'duration',
                  'place')

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
        activity = data.get('activity')
        if not Activity.objects.filter(name=activity.get('name')).exists():
            raise serializers.ValidationError(
                {'Ошибка': 'Такого вида активности не существует.'}
            )

    def create(self, validated_data):
        activity = validated_data.pop('activity')
        event = EventPost.objects.create(**validated_data)

        activity_name = Activity.objects.get(
            name=activity.get('name')
        )
        event.activity = activity_name
        event.save()

        return event

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get(
            'text',
            instance.text
        )
        instance.duration = validated_data.get(
            'duration',
            instance.duration
        )
        instance.date = validated_data.get(
            'date',
            instance.date
        )
        instance.place = validated_data.get(
            'place',
            instance.place
        )
        activity = validated_data.pop('activity')
        instance.activity.clear()
        activity_name = Activity.objects.get_or_create(
            name=activity.get('name')
        )
        instance.activity = activity_name
        instance.save()

        return instance

    def to_representation(self, instance):
        request = {'request': self.context.get('request')}
        post_for_view = EventPostGetSerializer(instance, context=request)
        return post_for_view.data


class EventPostShortSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра краткой информации о мероприятии на
    странице пользователя."""
    author = CustomUserSerializer(read_only=True)
    events = serializers.SerializerMethodField()
