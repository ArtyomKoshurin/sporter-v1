from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from .models import (Activity,
                     Event,
                     FavoriteEvent,
                     Participation,
                     Like)

from .serializers import (ActivitySerializer,
                          EventSerializer,
                          CommentSerializer)

from .permissions import IsAdminAuthorOrReadOnly
from .pagination import CustomPaginator
from .filters import EventFilter, ActivityFilter
from users.utils import create_relation, delete_relation


class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для просмотра видов активности."""
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ActivityFilter


class EventViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с постами мероприятий."""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EventFilter

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
            permission_classes=[permissions.IsAuthenticated, ])
    def favorite(self, request, pk):
        if request.method == 'POST':
            return create_relation(request,
                                   Event,
                                   FavoriteEvent,
                                   pk,
                                   EventSerializer,
                                   'event')
        return delete_relation(request,
                               Event,
                               FavoriteEvent,
                               pk,
                               'event')

    @action(methods=['POST', 'DELETE'],
            detail=True,
            permission_classes=[permissions.IsAuthenticated, ])
    def participate(self, request, pk):
        if request.method == 'POST':
            return create_relation(request,
                                   Event,
                                   Participation,
                                   pk,
                                   EventSerializer,
                                   'event')
        return delete_relation(request,
                               Event,
                               Participation,
                               pk,
                               'event')


class CommentViewSet(viewsets.ModelViewSet):
    """Сериализатор для комментариев к постам."""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPaginator

    def get_queryset(self):
        post = get_object_or_404(Event, id=self.kwargs['event_id'])
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
        event = get_object_or_404(Event, id=self.kwargs['event_id'])
        serializer.save(author=self.request.user, event=event)

    @action(methods=['POST', 'DELETE'],
            detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def like(self, request, event_id, pk):
        event = get_object_or_404(Event, id=event_id)
        comment = event.comments.get(id=pk)
        like = Like.objects.filter(user=request.user, comment=comment)

        if request.method == 'POST':
            if like.exists():
                return Response('Вы уже оценили этот комментарий.',
                                status=status.HTTP_400_BAD_REQUEST)
            Like.objects.create(user=request.user, comment=comment)
            serializer = CommentSerializer(comment,
                                           context={'request': request})

            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)

        if not like.exists():
            return Response('Вы еще не оценили этот комментарий.',
                            status=status.HTTP_400_BAD_REQUEST)
        like.delete()
        return Response(data=self.get_serializer(comment).data,
                        status=status.HTTP_204_NO_CONTENT)
