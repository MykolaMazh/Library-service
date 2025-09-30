from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema

from books.models import Book, Author
from books.permissions import IsAdminOrReadOnly
from books.serializers import (
    BookSerializer,
    AuthorSerializer,
    BookRetrieveSerializer,
)


@extend_schema(
    summary="Books of library",
    description="only admin users can edit. For users only get-requests available",
)
class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BookRetrieveSerializer
        return BookSerializer


@extend_schema(
    summary="Authors of Books in library",
    description="only admin users can edit. For users only get-requests available",
)
class AuthorViewSet(ModelViewSet):
    serializer_class = AuthorSerializer
    queryset = Author.objects.all()
    permission_classes = [IsAdminOrReadOnly]
