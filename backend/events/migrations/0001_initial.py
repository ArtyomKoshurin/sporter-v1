# Generated by Django 4.2.5 on 2023-11-28 19:03

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=124, unique=True, verbose_name='Вид спорта')),
            ],
            options={
                'verbose_name': 'Вид активности',
                'verbose_name_plural': 'Виды активностей',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ActivityForEventPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events_for_activity', to='events.activity')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(2000)], verbose_name='Текст')),
                ('pub_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата публикации')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='Автор комментария')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='EventPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=124, verbose_name='Название мероприятия')),
                ('text', models.TextField(verbose_name='Описание мероприятия')),
                ('datetime', models.DateTimeField(verbose_name='Дата и время проведения мероприятия')),
                ('duration', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Длительность мероприятия (мин)')),
                ('location', models.CharField(max_length=256, verbose_name='Место проведения')),
                ('activity', models.ManyToManyField(through='events.ActivityForEventPost', to='events.activity', verbose_name='Вид активности мероприятия')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_author', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-datetime'],
            },
        ),
        migrations.CreateModel(
            name='Participation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users_participation_for_event', to='events.eventpost', verbose_name='Мероприятие')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events_participation_for_user', to=settings.AUTH_USER_MODEL, verbose_name='Участник')),
            ],
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users_for_liked_comment', to='events.comment', verbose_name='Комментарий')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments_liked_for_user', to=settings.AUTH_USER_MODEL, verbose_name='Участник')),
            ],
        ),
        migrations.CreateModel(
            name='FavoriteActivity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users_for_activity', to='events.activity')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities_for_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='eventpost',
            name='participants',
            field=models.ManyToManyField(through='events.Participation', to=settings.AUTH_USER_MODEL, verbose_name='Участники'),
        ),
        migrations.AddField(
            model_name='comment',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='events.eventpost', verbose_name='Комментарий к посту'),
        ),
        migrations.AddField(
            model_name='comment',
            name='likes',
            field=models.ManyToManyField(through='events.Like', to=settings.AUTH_USER_MODEL, verbose_name='Лайки'),
        ),
        migrations.AddField(
            model_name='activityforeventpost',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities_for_event', to='events.eventpost'),
        ),
        migrations.AddConstraint(
            model_name='participation',
            constraint=models.UniqueConstraint(fields=('user', 'event'), name='unique_participation'),
        ),
        migrations.AddConstraint(
            model_name='like',
            constraint=models.UniqueConstraint(fields=('user', 'comment'), name='unique_like'),
        ),
        migrations.AddConstraint(
            model_name='favoriteactivity',
            constraint=models.UniqueConstraint(fields=('user', 'activity'), name='unique_activity_for_user'),
        ),
        migrations.AddConstraint(
            model_name='activityforeventpost',
            constraint=models.UniqueConstraint(fields=('event', 'activity'), name='unique_activity_for_event'),
        ),
    ]
