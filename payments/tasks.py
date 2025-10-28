from datetime import date

import stripe
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from celery import shared_task

from payments.models import Payment
from payments.helpers import create_stripe_payment
from borrowings.tasks import overdue_borrowings


@shared_task
def check_payment_session():
    queryset = Payment.objects.filter(status="pending")
    if queryset:
        for payment in queryset:
            session = stripe.checkout.Session.retrieve(payment.session_id)
            if session.expires_at < timezone.now().timestamp():
                create_stripe_payment(
                    payment.borrowing, payment.money_to_pay, payment.type
                )
                payment.status = Payment.StatusChoices.EXPIRED
                payment.save()
    return queryset
