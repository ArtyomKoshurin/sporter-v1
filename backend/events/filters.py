import datetime

from django.contrib.auth import get_user_model

from django_filters.rest_framework import (BooleanFilter,
                                           CharFilter,
                                           FilterSet,
                                           ModelMultipleChoiceFilter,
                                           NumberFilter)

from .models import Activity, Event


class ActivityFilter(FilterSet):
    """Фильтр для поиска вида активности по первым символам."""
    name = CharFilter(lookup_expr='startswith')

    class Meta:
        model = Activity
        fields = ['name']


class EventFilter(FilterSet):
    """Фильтр для постов по полю 'участвую', по автору поста,
    по актуальности мероприятия."""
    author = ModelMultipleChoiceFilter(
        field_name='author__username',
        to_field_name='username',
        queryset=get_user_model().objects.all()
    )
    activities = ModelMultipleChoiceFilter(
        field_name='activity__name',
        to_field_name='name',
        queryset=Activity.objects.all()
    )
    in_my_participation_list = BooleanFilter(
        field_name='users_participation_for_event',
        method='is_exist_filter'
    )
    is_actual_event = NumberFilter(
        method='is_actual_event_filter'
    )
    is_past_event = NumberFilter(
        method='is_past_event_filter'
    )
    is_actual_participation = BooleanFilter(
        field_name='users_participation_for_event',
        method='is_actual_participation_filter'
    )
    is_past_participation = BooleanFilter(
        field_name='users_participation_for_event',
        method='is_past_participation_filter'
    )

    class Meta:
        model = Event
        fields = ['activity', 'author']

    def is_exist_filter(self, queryset, name, value):
        lookup = '__'.join([name, 'user'])
        if self.request.user.is_anonymous:
            return queryset
        return queryset.filter(**{lookup: self.request.user})

    def is_actual_event_filter(self, queryset, name, value):
        if bool(value):
            return queryset.filter(
                datetime__gt=datetime.datetime.now()
            )
        return queryset

    def is_past_event_filter(self, queryset, name, value):
        if bool(value):
            return queryset.filter(
                datetime__lte=datetime.datetime.now()
            )
        return queryset

    def is_actual_participation_filter(self, queryset, name, value):
        lookup = '__'.join([name, 'user'])
        if self.request.user.is_anonymous:
            return queryset
        return queryset.filter(**{lookup: self.request.user},
                               datetime__gt=datetime.datetime.now())

    def is_past_participation_filter(self, queryset, name, value):
        lookup = '__'.join([name, 'user'])
        if self.request.user.is_anonymous:
            return queryset
        return queryset.filter(**{lookup: self.request.user},
                               datetime__lte=datetime.datetime.now())
