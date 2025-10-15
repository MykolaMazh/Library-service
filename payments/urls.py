from django.urls import path

from payments.views import PaymentListApiView, PaymentRetrieveUpdateApiView

urlpatterns = [
    path("", PaymentListApiView.as_view(), name="payment-list"),
    path(
        "<int:pk>/",
        PaymentRetrieveUpdateApiView.as_view(),
        name="payment-detail",
    ),
]


app_name = "payments"
