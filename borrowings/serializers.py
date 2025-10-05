from datetime import date
from rest_framework import serializers
from django.contrib.auth import get_user_model


from borrowings.models import Borrowing


User = get_user_model()


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.StringRelatedField()

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request.method == "GET" and request.user.is_staff:
            self.fields["user"] = serializers.StringRelatedField()
            self.fields["user_id"] = serializers.PrimaryKeyRelatedField(
                queryset=User.objects.all()
            )


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "book",
            "expected_return_date",
        ]

    def validate_book(self, book):
        if book.inventory == 0:
            raise serializers.ValidationError(
                "This book is currently unavailable (no inventory)."
            )
        return book

    def validate_expected_return_date(self, expected_return_date):
        if expected_return_date < date.today():
            raise serializers.ValidationError(
                "Return date cannot be earlier than actual date."
            )
        return expected_return_date
