from rest_framework import serializers
from books.models import Book, Author


class BookSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Book
        fields = ["id", "title", "author", "cover", "inventory", "daily_fee"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")
        if request and request.method in ["POST", "PUT", "PATCH"]:
            self.fields["author"] = serializers.PrimaryKeyRelatedField(
                queryset=Author.objects.all()
            )


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = [
            "id",
            "first_name",
            "last_name",
        ]
