from django.contrib import admin

from .models import (Activity,
                     ActivityForEventPost,
                     Comment,
                     EventPost,
                     FavoriteActivity,
                     Participation)

class ActivityInEventPost(admin.TabularInline):
    model = ActivityForEventPost
    min_num = 1


class FavoriteInActivity(admin.TabularInline):
    model = FavoriteActivity
    min_num = 1


class InParticipation(admin.TabularInline):
    model = Participation
    min_num = 1


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'name')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(ActivityForEventPost)
class ActivityForUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'activity', 'event')
    list_filter = ('activity',)


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


@admin.register(EventPost)
class EventPostAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'name',
                    'author',
                    'datetime')
    list_display_links = ('name',)
    search_fields = ('author',)
    list_filter = ('author',)
    empty_value_display = '-пусто-'

    inlines = [ActivityInEventPost, InParticipation]


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'user')
    list_filter = ('event',)
