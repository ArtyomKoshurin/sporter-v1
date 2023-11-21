from rest_framework.pagination import PageNumberPagination


class CustomPaginator(PageNumberPagination):
    """Кастомный пагинатор для вывода определенного количества объектов."""
    page_size = 10
