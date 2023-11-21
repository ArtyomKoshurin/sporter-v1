from django_filters import rest_framework

from .models import Activity


class ActivityFilter(rest_framework.FilterSet):
    """Фильтр для поиска вида активности по первым символам."""
    name = rest_framework.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Activity
        fields = ['name']
