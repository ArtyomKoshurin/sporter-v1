# Generated by Django 4.2.5 on 2023-11-30 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_rename_text_eventpost_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventpost',
            name='duration',
            field=models.PositiveIntegerField(verbose_name='Длительность мероприятия (мин)'),
        ),
    ]
