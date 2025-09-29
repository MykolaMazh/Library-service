from rest_framework import serializers
from django.contrib.auth import get_user_model

from borrowings.models import Borrowing


User = get_user_model()


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.StringRelatedField()
    user = serializers.StringRelatedField()
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "book",
            "user",
            "user_id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
        ]


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "book",
            "borrow_date",
            "expected_return_date",
        ]

    def validate_book(self, book):
        if book.inventory == 0:
            raise serializers.ValidationError(
                "This book is currently unavailable (no inventory)."
            )
        return book
