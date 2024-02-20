from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from .models import (Activity,
                     ActivityForEvent,
                     Comment,
                     Event,
                     FavoriteEvent,
                     Like,
                     Location,
                     Participation)


class ActivityInEvent(admin.TabularInline):
    model = ActivityForEvent
    min_num = 1


class InParticipation(admin.TabularInline):
    model = Participation
    min_num = 1


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'

@admin.register(Location)
class LocationAdmin(OSMGeoAdmin):
    list_display = ('id', 'address', 'point')
    list_display_links = ('address',)
    search_fields = ('address',)
    list_filter = ('address',)
    empty_value_display = '-пусто-'


@admin.register(ActivityForEvent)
class ActivityForEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'activity', 'event')
    list_filter = ('activity',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'name',
                    'author',
                    'datetime')
    list_display_links = ('name',)
    search_fields = ('author',)
    list_filter = ('author',)
    empty_value_display = '-пусто-'

    inlines = [ActivityInEvent, InParticipation]


@admin.register(FavoriteEvent)
class FavoriteEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'user' )
    list_filter = ('event',)


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'user')
    list_filter = ('event',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'text',
                    'event',
                    'author',
                    'pub_date')
    list_display_links = ('event',)
    search_fields = ('author',)
    list_filter = ('author',)
    empty_value_display = '-пусто-'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'comment', 'user')
    list_filter = ('comment',)
