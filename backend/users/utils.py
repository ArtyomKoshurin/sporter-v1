from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response


def create_relation(request, model, model_relation, pk, serializer, field):
    """Функция создания связи User - Model."""

    model_obj = get_object_or_404(model, pk=pk)
    model_relation_obj = model_relation.objects.filter(
        user=request.user, **{field: model_obj}
    )

    if not model_relation_obj.exists():
        model_relation.objects.create(user=request.user,
                                      **{field: model_obj})
        serializer = serializer(model_obj, context={'request': request})
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)
    return Response(
        data={'errors': 'Попытка повторного добавления объекта'},
        status=status.HTTP_400_BAD_REQUEST
    )


def delete_relation(request, model, model_relation, pk, field):
    """Функция удаления связи User - Model."""

    model_obj = get_object_or_404(model, pk=pk)
    model_relation_obj = model_relation.objects.filter(
        user=request.user, **{field: model_obj}
    )

    if model_relation_obj.exists():
        model_relation_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(
        data={'errors': 'Попытка удаления несуществующего объекта'},
        status=status.HTTP_404_NOT_FOUND
    )
