from django.contrib.auth import get_user_model

from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from .models import (Activity,
                     EventPost,
                     Participation,
                     Comment,
                     Like)
from .serializers import (ActivitySerializer,
                          EventSerializer,
                          CommentSerializer)

from users.serializers import CustomUserSerializer

from .permissions import IsAdminAuthorOrReadOnly
from .pagination import CustomPaginator


class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для просмотра видов активности."""
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class EventViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с постами мероприятий."""
    queryset = EventPost.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [permissions.AllowAny]
        elif self.request.method in ['PATCH', 'DELETE']:
            self.permission_classes = [IsAdminAuthorOrReadOnly]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    @action(methods=['POST', 'DELETE'],
            detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def participate(self, request, pk):
        event = get_object_or_404(EventPost, id=pk)
        participation = Participation.objects.filter(
                user=request.user, event=event
        )

        if request.method == 'POST':
            if participation.exists():
                return Response('Вы уже идете на это мероприятие.',
                                status=status.HTTP_400_BAD_REQUEST)
            Participation.objects.create(user=request.user, event=event)
            serializer = EventSerializer(event, context={'request': request})
            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)
        if not participation.exists():
            return Response(
                'Вы еще не подписались на участие в данном мероприятии',
                status=status.HTTP_400_BAD_REQUEST
            )
        participation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(viewsets.ModelViewSet):
    """Сериализатор для комментариев к постам."""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPaginator

    def get_queryset(self):
        post = get_object_or_404(EventPost, id=self.kwargs['event_id'])
        return post.comments.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [permissions.AllowAny]
        elif self.request.method == 'PATCH' or self.request.method == 'DELETE':
            self.permission_classes = [IsAdminAuthorOrReadOnly]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        event = get_object_or_404(EventPost, id=self.kwargs['event_id'])
        serializer.save(author=self.request.user, event=event)

    @action(methods=['POST', 'DELETE'],
            detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def like(self, request, event_id, pk):
        event = get_object_or_404(EventPost, id=event_id)
        comment = event.comments.get(id=pk)
        like = Like.objects.filter(user=request.user, comment=comment)

        if request.method == 'POST':
            if like.exists():
                return Response('Вы уже оценили этот комментарий.',
                                status=status.HTTP_400_BAD_REQUEST)
            Like.objects.create(user=request.user, comment=comment)
            serializer = CommentSerializer(like, {'request': request})
            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)

        if not like.exists():
            return Response('Вы еще не оценили этот комментарий.',
                            status=status.HTTP_400_BAD_REQUEST)
        like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
