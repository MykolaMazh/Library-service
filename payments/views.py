from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response,
import stripe

from borrowings.models import Borrowing
from payments.models import Payment
from payments.serializers import (
    PaymentListSerializer,
    PaymentRetrieveUpdateSerializer,
)
from payments.permissions import IsBorrower


class PaymentListApiView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(borrowing__user=self.request.user)


class PaymentRetrieveUpdateApiView(generics.RetrieveUpdateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentRetrieveUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return Payment.objects.filter(borrowing__user=self.request.user)


stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(APIView):
    def post(self, request, borrowing_id):
        borrowing = get_object_or_404(Borrowing, id=borrowing_id)
        amount = int(borrowing.total_price * 100)  # amount in cents

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                mode="payment",
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": f"Borrowing #{borrowing.id}"
                            },
                            "unit_amount": amount,
                        },
                        "quantity": 1,
                    }
                ],
                success_url="https://yourfrontend.com/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url="https://yourfrontend.com/cancel",
            )

            # Save Payment to DB
            payment = Payment.objects.create(
                borrowing=borrowing,
                money_to_pay=borrowing.total_price,
                session_id=checkout_session.id,
                session_url=checkout_session.url,
                status=Payment.StatusChoices.PENDING,
                type=Payment.TypeChoices.PAYMENT,
            )

            return Response(
                {"checkout_url": payment.session_url},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
