from datetime import date
from rest_framework import serializers
from django.contrib.auth import get_user_model


from borrowings.models import Borrowing


User = get_user_model()


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.StringRelatedField()
    payments = serializers.SerializerMethodField()

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "payments",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request.method == "GET" and request.user.is_staff:
            self.fields["user"] = serializers.StringRelatedField()
            self.fields["user_id"] = serializers.PrimaryKeyRelatedField(
                queryset=User.objects.all()
            )

    def get_payments(self, obj):
        return [
            {
                "payment_id": payment.id,
                "to be paid": payment.money_to_pay,
                "payment_type": payment.type,
                "payment_status": payment.status,
            }
            for payment in obj.payment_set.exclude(status="expired")
        ]


class BorrowingRetrieveSerializer(BorrowingListSerializer):
    payments = serializers.SerializerMethodField()

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "payments",
        ]

    def get_payments(self, obj):
        return [
            {
                "payment_id": payment.id,
                "status": payment.status,
                "type": payment.type,
                "to be paid": payment.money_to_pay,
            }
            for payment in obj.payment_set.all()
        ]


class BorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = ["book", "expected_return_date"]

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
