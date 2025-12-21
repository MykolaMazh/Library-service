from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from books.models import Book, Author


class BookRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "cover",
            "inventory",
            "daily_fee",
            "synopsis",
        ]


class BookSerializer(BookRetrieveSerializer):
    author = serializers.StringRelatedField()

    class Meta(BookRetrieveSerializer.Meta):
        validators = [
            UniqueTogetherValidator(
                queryset=Book.objects.all(),
                fields=["title", "author"],
                message="This author already has a book with this title.",
            )
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request:
            if request.method in ["POST", "PUT", "PATCH"]:
                self.fields["author"] = serializers.PrimaryKeyRelatedField(
                    queryset=Author.objects.all()
                )
            elif request.method == "GET":
                self.fields["synopsis"] = serializers.SerializerMethodField()

    def get_synopsis(self, obj):
        words = obj.synopsis.split()
        return " ".join(words[:15]) + ("..." if len(words) > 15 else "")


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = [
            "id",
            "first_name",
            "last_name",
        ]
