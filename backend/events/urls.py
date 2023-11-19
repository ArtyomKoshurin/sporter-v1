from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ActivityViewSet, EventViewSet, CommentViewSet

app_name = 'events'

router_events_v1 = DefaultRouter

router_events_v1.register('activity', ActivityViewSet, basename='activity')
router_events_v1.register('events', EventViewSet, basename='events')
router_events_v1.register(
    r'events/(?P<post_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('', include(router_events_v1.urls)),
]
