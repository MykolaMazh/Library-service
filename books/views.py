from rest_framework.viewsets import ModelViewSet

from books.models import Book, Author
from books.permissions import IsAdminOrReadOnly
from books.serializers import BookSerializer, AuthorSerializer


class BookViewSet(ModelViewSet):
    serializer_class = BookSerializer
    queryset = Book.objects.all()
    permission_classes = [IsAdminOrReadOnly]




class AuthorViewSet(ModelViewSet):
    serializer_class = AuthorSerializer
    queryset = Author.objects.all()
    permission_classes = [IsAdminOrReadOnly]
