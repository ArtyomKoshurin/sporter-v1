from django.urls import include, path
from rest_framework import routers

from .views import CustomUserViewSet

app_name = 'users'

router_users_v1 = routers.DefaultRouter()

router_users_v1.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router_users_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
