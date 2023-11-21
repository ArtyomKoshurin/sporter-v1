import datetime

from django_filters import rest_framework

from .models import Activity


class ActivityFilter(rest_framework.FilterSet):
    """Фильтр для поиска вида активности по первым символам."""
    name = rest_framework.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Activity
        fields = ['name']


class EventPostsFilter(rest_framework.FilterSet):
    """Фильтр для постов по полю 'участвую', по автору поста,
    по актуальности мероприятия."""
    author = rest_framework.NumberFilter(
        field_name='author',
        lookup_expr='exact'
    )
    is_past = rest_framework.NumberFilter(
        method='filter_is_past'
    )
    is_actual = rest_framework.NumberFilter(
        method='filter_is_actual'
    )
    in_my_activities = rest_framework.NumberFilter(
        method='filter_in_my_activities'
    )
    is_user_past = rest_framework.NumberFilter(
        method='filter_is_user_past'
    )
    is_user_actual = rest_framework.NumberFilter(
        method='filter_is_user_actual'
    )

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

    def filter_in_my_activities(self, queryset, name, value):
        activity_range = []
        for activity in self.request.user.activity:
            activity_range.append(activity.get('name'))

        if bool(value):
            return queryset.filter(
                activity__name__range=activity_range
            )

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
