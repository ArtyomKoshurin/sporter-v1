from django.contrib import admin

from .models import CustomUser, Subscribe, FavoriteActivity


class FavoriteInActivity(admin.TabularInline):
    model = FavoriteActivity
    min_num = 1


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'username',
                    'email',
                    'first_name',
                    'last_name',
                    'date_joined',
                    'phone_number')
    list_display_links = ('username',)
    search_fields = ('username',)
    list_filter = ('username', 'email')
    empty_value_display = '-пусто-'

    inlines = [FavoriteInActivity]


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    list_filter = ('user',)
