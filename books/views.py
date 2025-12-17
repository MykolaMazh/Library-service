from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema, OpenApiExample

from books.models import Book, Author
from books.permissions import IsAdminOrReadOnly
from books.serializers import (
    BookSerializer,
    AuthorSerializer,
    BookRetrieveSerializer,
)


@extend_schema(
    summary="Books of library",
    description="only admin users can edit. "
    "For users only get-requests available",
)
class BookViewSet(ModelViewSet):
    queryset = Book.objects.filter(inventory__gt=0)
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BookRetrieveSerializer
        return BookSerializer

    @extend_schema(
        summary="Create a new book",
        description="Admin user can add new books.",
        request=BookSerializer(),
        examples=[
            OpenApiExample(
                name="Request example",
                description='"Cover" is choice from "HARD"/"SOFT" '
                'by default is set to "HARD"',
                value={
                    "author": 4,
                    "title": "Into the Water",
                    "cover": "SOFT",
                    "synopsis": '"Into The Water" by Paula Hawkins is an'
                    " addictive psychological suspense novel that delves"
                    " into the slipperiness of truth"
                    " and a family drowning in secrets.\n\n",
                    "inventory": 2,
                    "daily_fee": "1.35",
                },
                request_only=True,
            )
        ],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


@extend_schema(
    summary="Authors of Books in library",
    description="only admin users can edit."
    " For users only get-requests available",
)
class AuthorViewSet(ModelViewSet):
    serializer_class = AuthorSerializer
    queryset = Author.objects.all()
    permission_classes = [IsAdminOrReadOnly]
