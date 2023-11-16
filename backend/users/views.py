from djoser.views import UserViewSet

from rest_framework import permissions

from .serializers import CustomUserSerializer

from .models import CustomUser


class CustomUserViewSet(UserViewSet):
    """Кастомный вьюсет Пользователя."""
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [permissions.IsAuthenticated, ]
        return super().get_permissions()
