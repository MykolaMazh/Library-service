from django.urls import path

from payments.views import (
    PaymentListApiView,
    PaymentRetrieveUpdateApiView,
    PaymentCancelRedirectView,
)
from payments.views import PaymentSuccessRedirectView

urlpatterns = [
    path("", PaymentListApiView.as_view(), name="payment-list"),
    path(
        "<int:pk>/",
        PaymentRetrieveUpdateApiView.as_view(),
        name="payment-detail",
    ),
    path(
        "success/",
        PaymentSuccessRedirectView.as_view(),
        name="payment-completed",
    ),
    path(
        "cancel/",
        PaymentCancelRedirectView.as_view(),
        name="payment-cancelled",
    ),
]


app_name = "payments"
