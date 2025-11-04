from django.conf import settings
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import stripe

from notifications.telegram_helper import send_successfull_payment_notification
from payments.models import Payment
from payments.serializers import (
    PaymentListSerializer,
    PaymentRetrieveUpdateSerializer,
)


stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentListApiView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Payment.objects.select_related(
            "borrowing", "borrowing__book"
        )
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(borrowing__user=self.request.user)


class PaymentRetrieveUpdateApiView(generics.RetrieveUpdateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentRetrieveUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return Payment.objects.filter(borrowing__user=self.request.user)


class PaymentSuccessRedirectView(APIView):
    """Url Stripe automatically redirect to after a payment is
    completed successfully. Marks
    payment_status as 'paid'."""

    def get(self, request):
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response(
                {"error": "Missing session_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            session = stripe.checkout.Session.retrieve(session_id)

            if session.payment_status == "paid":
                payment = Payment.objects.filter(session_id=session_id).first()
                if payment:
                    old_status = payment.status
                    payment.status = Payment.StatusChoices.PAID
                    payment.save()
                    if old_status != payment.status:
                        send_successfull_payment_notification(payment)
                return Response(
                    {"message": "The payment has been successfully completed!"}
                )
            else:
                return Response(
                    {"message": "Your payment has not been completed yet."}
                )
        except stripe.StripeError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class PaymentCancelRedirectView(APIView):
    """Url the user is redirected to if cancelled the payment."""

    def get(self, request):
        return Response(
            {
                "message": "Your payment was not completed (or interrupted)."
                " You still have 24 hours to complete your payment before "
                "the session expires."
            }
        )
