import datetime

from django_filters.rest_framework import (BooleanFilter,
                                           CharFilter,
                                           FilterSet,
                                           ModelMultipleChoiceFilter,
                                           NumberFilter)

from .models import Activity, EventPost


class ActivityFilter(FilterSet):
    """Фильтр для поиска вида активности по первым символам."""
    name = CharFilter(lookup_expr='startswith')

    class Meta:
        model = Activity
        fields = ['name']


class EventPostsFilter(FilterSet):
    """Фильтр для постов по полю 'участвую', по автору поста,
    по актуальности мероприятия."""
    author = NumberFilter(
        field_name='author',
        lookup_expr='exact'
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
    in_my_activities = BooleanFilter(
        field_name='activities_for_event__activity__users_for_activity',
        method='is_exist_filter'
    )

    # in_my_activities = NumberFilter(
    #     method='filter_in_my_activities'
    # )

    is_past = NumberFilter(
        method='filter_is_past'
    )
    is_actual = NumberFilter(
        method='filter_is_actual'
    )
    is_user_past = NumberFilter(
        method='filter_is_user_past'
    )
    is_user_actual = NumberFilter(
        method='filter_is_user_actual'
    )

    class Meta:
        model = EventPost
        fields = ['activity', 'author']

    def is_exist_filter(self, queryset, name, value):
        lookup = '__'.join([name, 'user'])
        if self.request.user.is_anonymous:
            return queryset
        return queryset.filter(**{lookup: self.request.user})

    def filter_is_past(self, queryset, name, value):
        if bool(value):
            return queryset.filter(
                datetime__lte=datetime.datetime.now()
            )
        return queryset

    def filter_is_actual(self, queryset, name, value):
        if bool(value):
            return queryset.filter(
                datetime__gt=datetime.datetime.now()
            )
        return queryset

    # def filter_in_my_activities(self, queryset, name, value):
    #     activity_range = []
    #     for activity in self.request.user.activity:
    #         activity_range.append(activity.get('name'))

    #     if bool(value):
    #         return queryset.filter(
    #             activity__name__range=activity_range
    #         )

    def filter_is_user_past(self, queryset, name, value):
        if bool(value):
            return queryset.filter(
                datetime__lte=datetime.datetime.now(),
                activity_for_user__user=self.request.user
            )
        return queryset

    def filter_is_user_actual(self, queryset, name, value):
        if bool(value):
            return queryset.filter(
                datetime__gt=datetime.datetime.now(),
                activity_for_user__user=self.request.user
            )
        return queryset
