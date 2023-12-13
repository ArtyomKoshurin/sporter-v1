# Generated by Django 4.2.5 on 2023-12-12 13:31

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_alter_activity_options_alter_activity_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=256, verbose_name='Адрес')),
                ('point', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
            options={
                'verbose_name': 'Место проведения',
                'verbose_name_plural': 'Места проведения',
                'ordering': ['address'],
            },
        ),
        migrations.RemoveField(
            model_name='event',
            name='location',
        ),
        migrations.CreateModel(
            name='LocationForEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locations_for_event', to='events.event')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events_for_location', to='events.location')),
            ],
            options={
                'verbose_name_plural': 'Локация - Мероприятие',
            },
        ),
        migrations.AddField(
            model_name='event',
            name='location',
            field=models.ManyToManyField(through='events.LocationForEvent', to='events.location', verbose_name='Место проведения мероприятия'),
        ),
        migrations.AddConstraint(
            model_name='locationforevent',
            constraint=models.UniqueConstraint(fields=('event', 'location'), name='unique_location_for_event'),
        ),
    ]
