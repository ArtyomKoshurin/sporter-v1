from django.shortcuts import get_object_or_404

from djoser.views import UserViewSet

from rest_framework import permissions
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import CustomUserSerializer

from .models import CustomUser, Subscribe

from .utils import create_relation, delete_relation


class CustomUserViewSet(UserViewSet):
    """Кастомный вьюсет Пользователя."""
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.IsAuthenticated,]

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [permissions.IsAuthenticated, ]
        return super().get_permissions()

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=[permissions.IsAuthenticated, ])
    def subscribe(self, request, id):
        author = get_object_or_404(CustomUser, pk=id)
        if request.user != author:
            if request.method == 'POST':
                return create_relation(request,
                                       CustomUser,
                                       Subscribe,
                                       id,
                                       CustomUserSerializer,
                                       field='author')
            return delete_relation(request,
                                   CustomUser,
                                   Subscribe,
                                   id,
                                   field='author')
        return Response(
            data={'errors': 'Подписка на самого себя запрещена'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False,
            permission_classes=[permissions.IsAuthenticated, ])
    def subscriptions(self, request):
        subscribers_data = CustomUser.objects.filter(
            subscribers__user=request.user
        )
        page = self.paginate_queryset(subscribers_data)
        serializer = CustomUserSerializer(
            page, many=True, context={'request': request}
        )

        return self.get_paginated_response(serializer.data)
