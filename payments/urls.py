from django.urls import path

from payments.views import PaymentListApiView, PaymentRetrieveUpdateApiView
from payments.views import CreateCheckoutSessionView

urlpatterns = [
    path("", PaymentListApiView.as_view(), name="payment-list"),
    path(
        "<int:pk>/",
        PaymentRetrieveUpdateApiView.as_view(),
        name="payment-detail",
    ),
    path(
        "create-payment/<int:borrowing_id>/",
        CreateCheckoutSessionView.as_view(),
        name="create-payment-session",
    ),
]


app_name = "payments"
