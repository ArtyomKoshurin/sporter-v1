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
    EventSerializer,
    CommentSerializer
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
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [permissions.AllowAny]
        elif self.request.method == 'PATCH' or self.request.method == 'DELETE':
            self.permission_classes = [IsAdminAuthorOrReadOnly]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    @action(methods=['POST', 'DELETE'], detail=False,
            url_path=r'(?P<event_id>\d+)/participate',
            permission_classes=(permissions.IsAuthenticated,))
    def participate(self, request, **kwargs):
        event = get_object_or_404(EventPost, id=kwargs['event_id'])

        participation = Participation.objects.filter(
                user=request.user, event=event
        )

        if request.method == 'POST':
            if participation.exists():
                return Response('Вы уже идете на это мероприятие.',
                                status=status.HTTP_400_BAD_REQUEST)
            Participation.objects.create(user=request.user, event=event)
            serializer = serializer(event)
            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)

        if not participation.exists():
            return Response('Вы еще не подписались '
                            'на участие в данном мероприятии',
                            status=status.HTTP_400_BAD_REQUEST)
        participation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False,
            permission_classes=[permissions.IsAuthenticated, ])
    def participations(self, request):
        subscribers_data = CustomUser.objects.filter(
            subscribers__user=request.user
        )
        page = self.paginate_queryset(subscribers_data)
        serializer = CustomUserContextSerializer(
            page, many=True, context={'request': request}
        )

        return self.get_paginated_response(serializer.data)


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
        post = get_object_or_404(EventPost, id=self.kwargs['post_id'])
        serializer.save(author=self.request.user, post=post)

    @action(methods=['POST', 'DELETE'], detail=False,
            url_path=r'(?P<comment_id>\d+)/like',
            permission_classes=(permissions.IsAuthenticated,))
    def like(self, request, **kwargs):
        comment = get_object_or_404(Comment, id=kwargs['comment_id'])

        like = Like.objects.filter(user=request.user, comment=comment)

        if request.method == 'POST':
            if like.exists():
                return Response('Вы уже оценили этот комментарий.',
                                status=status.HTTP_400_BAD_REQUEST)
            Like.objects.create(user=request.user, comment=comment)
            serializer = serializer(like)
            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)

        if not like.exists():
            return Response('Вы еще не оценили этот комментарий.',
                            status=status.HTTP_400_BAD_REQUEST)
        like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
