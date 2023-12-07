from django.conf import settings
from django.db import models


class Activity(models.Model):
    """Модель видов спорта."""
    name = models.CharField(
        verbose_name='Вид спорта',
        max_length=124,
        unique=True
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Вид активности'
        verbose_name_plural = 'Виды активностей'

    def __str__(self):
        return self.name


class Event(models.Model):
    """Модель публикаций о мероприятиях."""
    name = models.CharField(
        verbose_name='Название мероприятия',
        max_length=124
    )
    description = models.TextField(verbose_name='Описание мероприятия')
    activity = models.ManyToManyField(
        Activity,
        through='ActivityForEvent',
        verbose_name='Вид активности мероприятия'
    )
    datetime = models.DateTimeField(
        verbose_name='Дата и время проведения мероприятия'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='event_author',
        on_delete=models.CASCADE
    )
    duration = models.PositiveIntegerField(
        verbose_name='Длительность мероприятия (мин)',
    )
    location = models.CharField(
        verbose_name='Место проведения',
        max_length=256
    )

    class Meta:
        ordering = ['-datetime']
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'

    def __str__(self):
        return self.name


class ActivityForEvent(models.Model):
    """Вспомогательная модель для связи 'вид спорта-мероприятие'."""
    event = models.ForeignKey(
        Event,
        related_name='activities_for_event',
        on_delete=models.CASCADE
    )
    activity = models.ForeignKey(
        Activity,
        related_name='events_for_activity',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name_plural = 'Активность - Мероприятие'
        constraints = [
            models.UniqueConstraint(
                fields=['event', 'activity'],
                name='unique_activity_for_event'
            )
        ]

    def __str__(self):
        return f'{self.event}: {self.activity}'


class Comment(models.Model):
    """Модель комментария к отзыву."""
    event = models.ForeignKey(
        Event,
        verbose_name='Комментарий к посту',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Автор комментария',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Like',
        verbose_name='Лайки'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text


class FavoriteEvent(models.Model):
    """Модель избранных мероприятий."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Участник',
        related_name='favorite_for_user',
        on_delete=models.CASCADE
    )
    event = models.ForeignKey(
        Event,
        verbose_name='Мероприятие',
        related_name='users_favorite_for_event',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name_plural = 'Избранные мероприятия'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'event'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return (f'Мероприятие {self.event} в избранном у пользователя  '
                f'{self.user.username}')


class Participation(models.Model):
    """Модель участия пользователя в мероприятии."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Участник',
        related_name='events_participation_for_user',
        on_delete=models.CASCADE
    )
    event = models.ForeignKey(
        Event,
        verbose_name='Мероприятие',
        related_name='users_participation_for_event',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name_plural = 'Участие в мероприятиях'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'event'],
                name='unique_participation'
            )
        ]

    def __str__(self):
        return (f'Пользователь {self.user.username} участвует в мероприятии'
                f'{self.event}')


class Like(models.Model):
    """Модель лайков комментариев."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Участник',
        related_name='comments_liked_for_user',
        on_delete=models.CASCADE
    )
    comment = models.ForeignKey(
        Comment,
        verbose_name='Комментарий',
        related_name='users_for_liked_comment',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'comment'],
                name='unique_like'
            )
        ]

    def __str__(self):
        return (f'Пользователь {self.user.username} оценил комментарий'
                f'{self.comment}')
