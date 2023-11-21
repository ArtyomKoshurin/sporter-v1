from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from .models import (
    Activity,
    EventPost,
    Participation,
    Comment,
    Like
)
from .serializers import (
    ActivitySerializer,
    EventGetSerializer,
    EventCreateSerializer,
    CommentCreateSerializer,
    CommentGetSerializer
)

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
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'participing']:
            return EventGetSerializer
        return EventCreateSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        elif self.request.method == 'PATCH' or self.request.method == 'DELETE':
            permission_classes = [IsAdminAuthorOrReadOnly]
        elif self.action == 'participing':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['POST', 'DELETE'], detail=False,
            url_path=r'(?P<post_id>\d+)/participing',
            permission_classes=(permissions.IsAuthenticated,))
    def participing(self, request, **kwargs):
        post = get_object_or_404(EventPost, id=kwargs['post_id'])

        if request.method == 'POST':
            if Participation.objects.filter(
                    user=request.user, post=post).exists():
                return Response('Вы уже идете на это мероприятие.',
                                status=status.HTTP_400_BAD_REQUEST)
            Participation.objects.create(user=request.user, post=post)
            return Response(data=self.get_serializer(post).data,
                            status=status.HTTP_201_CREATED)

        participing = Participation.objects.filter(
                user=request.user, post=post).first()
        if not participing:
            return Response('Вы еще не подписались '
                            'на участие в данном мероприятии',
                            status=status.HTTP_400_BAD_REQUEST)
        participing.delete()
        return Response(data=self.get_serializer(post).data,
                        status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(viewsets.ModelViewSet):
    """Сериализатор для комментариев к постам."""
    pagination_class = CustomPaginator

    def get_queryset(self):
        post = get_object_or_404(EventPost, id=self.kwargs['post_id'])
        return post.comments.all()

    def get_serializer_class(self):
        if self.request.method == 'GET' or self.action == 'like':
            return CommentGetSerializer
        return CommentCreateSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        elif self.request.method == 'PATCH' or self.request.method == 'DELETE':
            permission_classes = [IsAdminAuthorOrReadOnly]
        elif self.action == 'like':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        post = get_object_or_404(EventPost, id=self.kwargs['post_id'])
        serializer.save(author=self.request.user, post=post)

    @action(methods=['POST', 'DELETE'], detail=False,
            url_path=r'(?P<comment_id>\d+)/like',
            permission_classes=(permissions.IsAuthenticated,))
    def like(self, request, **kwargs):
        comment = get_object_or_404(Comment, id=kwargs['comment_id'])

        if request.method == 'POST':
            if Like.objects.filter(
                    user=request.user, comment=comment).exists():
                return Response('Вы уже оценили этот комментарий.',
                                status=status.HTTP_400_BAD_REQUEST)
            Like.objects.create(user=request.user, comment=comment)
            return Response(data=self.get_serializer(comment).data,
                            status=status.HTTP_201_CREATED)

        like = Like.objects.filter(
                user=request.user, comment=comment).first()
        if not like:
            return Response('Вы еще не оценили этот комментарий.',
                            status=status.HTTP_400_BAD_REQUEST)
        like.delete()
        return Response(data=self.get_serializer(comment).data,
                        status=status.HTTP_204_NO_CONTENT)
