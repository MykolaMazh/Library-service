from rest_framework import serializers

from borrowings.models import Borrowing
from payments.models import Payment


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


class PaymentListSerializer(serializers.ModelSerializer):
    borrowing = serializers.SerializerMethodField()
    _book_id = serializers.IntegerField(source="borrowing.book.id")

    class Meta:
        model = Payment
        fields = ["id", "status", "type", "borrowing", "_book_id"]

    def get_borrowing(self, instance):
        book = instance.borrowing.book.title
        expected_return_date = instance.borrowing.expected_return_date
        return {"book_id": book, "expected_return_date": expected_return_date}


class PaymentRetrieveUpdateSerializer(serializers.ModelSerializer):
    borrowing = BorrowingListSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay",
        ]
