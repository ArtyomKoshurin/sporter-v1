from rest_framework import serializers

from .models import (
    Activity,
    EventPost,
    Participation,
    Comment,
    Like
)


class ActivitySerializer(serializers.ModelSerializer):
    """Сериализатор для видов спорта."""
    class Meta:
        model = Activity
        fields = ('id', 'name')


class EventGetSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра постов о мероприятиях."""
    activity = ActivitySerializer(read_only=True)
    author = CustomUserSerializer(read_only=True)
    is_participing = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = EventPost
        fields = ('id', 'name', 'text', 'activity', 'date', 'author',
                  'duration', 'place', 'is_participing', 'comments')

    def get_is_participing(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False

        return Participation.objects.filter(
            post=obj, user=request.user).exists()

    def get_comments(self, obj):
        return Comment.objects.filter(post=obj).order_by('-id')[:3]


class EventCreateSerializer(serializers.ModelSerializer):
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
        fields = ('id', 'name', 'text', 'activity', 'date', 'author',
                  'duration', 'place')

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
        post_for_view = EventGetSerializer(instance, context=request)
        return post_for_view.data


class CommentGetSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра комментариев."""
    author = CustomUserSerializer(read_only=True)
    likes = serializers.SerializerMethodField()
    my_like = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'author', 'text', 'pub_date', 'post',
                  'my_like', 'likes')

    def get_my_like(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False

        return Like.objects.filter(comment=obj, user=request.user).exists()

    def get_likes(self, obj):
        return obj.like.count()


class CommentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания комментария к посту."""
    author = CustomUserSerializer(read_only=True)
    text = serializers.CharField(required=True, max_length=2000)
    pub_date = serializers.DateTimeField(auto_now_add=True, read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'author', 'text', 'pub_date', 'post')

    def validate_text(self, value):
        if len(value) > 2000:
            raise serializers.ValidationError(
                'Длина текста не должна превышать 2000 символов.'
            )
        return value

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        instance.save()

        return instance
