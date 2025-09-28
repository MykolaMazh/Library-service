from rest_framework import serializers

from borrowings.models import Borrowing


class BorrowingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "book",
            "user",
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
