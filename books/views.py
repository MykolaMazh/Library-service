from rest_framework.viewsets import ModelViewSet

from books.models import Book, Author
from books.permissions import IsAdminOrReadOnly
from books.serializers import (
    BookSerializer,
    AuthorSerializer,
    BookRetrieveSerializer,
)


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BookRetrieveSerializer
        return BookSerializer


class AuthorViewSet(ModelViewSet):
    serializer_class = AuthorSerializer
    queryset = Author.objects.all()
    permission_classes = [IsAdminOrReadOnly]
