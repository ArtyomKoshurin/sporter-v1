from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Activity(models.Model):
    """Модель видов спорта."""
    name = models.CharField(
        verbose_name='Название вида спорта',
        max_length=124,
        unique=True
    )

    def __str__(self):
        return self.name


class ActivityForUser(models.Model):
    """Вспомогательная модель для связи 'вид спорта-юзер'."""
    user = models.ForeignKey(
        CustomUser,
        related_name='activity_for_user',
        on_delete=models.CASCADE
    )
    activity = models.ForeignKey(
        Activity,
        related_name='activity_for_user',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'activity'],
                name='unique_activity_for_user'
            )
        ]

    def __str__(self):
        return f'{self.user}: {self.activity}'


class EventPost(models.Model):
    """Модель публикаций о мероприятиях."""
    name = models.CharField(
        verbose_name='Название мероприятия',
        max_length=124
    )
    text = models.TextField(verbose_name='Описание мероприятия')
    activity = models.ForeignKey(
        Activity,
        related_name='event_activity',
        verbose_name='Вид активности мероприятия',
        on_delete=models.CASCADE
    )
    datetime = models.DateTimeField(
        verbose_name='Дата и время проведения мероприятия'
    )
    author = models.ForeignKey(
        CustomUser,
        related_name='event_author',
        on_delete=models.CASCADE
    )
    duration = models.PositiveIntegerField(
        validators=MinValueValidator(1),
        verbose_name='Длительность мероприятия (мин)'
    )
    place = models.CharField(
        verbose_name='Место проведения',
        max_length=256
    )

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.name


class Comment(models.Model):
    """Модель комментария к отзыву."""
    post = models.ForeignKey(
        EventPost,
        verbose_name='Комментарий к посту',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        verbose_name='Текст',
        validators=[MinValueValidator(1), MaxValueValidator(2000)]
    )
    author = models.ForeignKey(
        CustomUser,
        verbose_name='Автор комментария',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ['-id']


class Participation(models.Model):
    """Модель участия пользователя в мероприятии."""
    user = models.ForeignKey(
        CustomUser,
        verbose_name='Участник',
        related_name='participation',
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        EventPost,
        verbose_name='Мероприятие',
        related_name='participation',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                name='unique_participation'
            )
        ]

    def __str__(self):
        return (f'Пользователь {self.user.username} участвует в мероприятии'
                f'{self.post}')


class Like(models.Model):
    """Модель лайков комментариев."""
    user = models.ForeignKey(
        CustomUser,
        verbose_name='Участник',
        related_name='like',
        on_delete=models.CASCADE
    )
    comment = models.ForeignKey(
        Comment,
        verbose_name='Комментарий',
        related_name='like',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'comment'],
                name='unique_like'
            )
        ]

    def __str__(self):
        return (f'Пользователь {self.user.username} оценил комментарий'
                f'{self.comment}')
