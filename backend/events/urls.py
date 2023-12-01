from django.urls import path, include
from rest_framework import routers

from .views import ActivityViewSet, EventViewSet, CommentViewSet

app_name = 'events'

router_events_v1 = routers.DefaultRouter()

router_events_v1.register('activities', ActivityViewSet, basename='activities')
router_events_v1.register('events', EventViewSet, basename='events')
router_events_v1.register(
    r'events/(?P<event_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('', include(router_events_v1.urls)),
]
