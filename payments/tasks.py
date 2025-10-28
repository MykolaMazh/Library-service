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
    updates_number = 0
    if queryset:
        for payment in queryset:
            session = stripe.checkout.Session.retrieve(payment.session_id)
            if session.expires_at < timezone.now().timestamp():
                create_stripe_payment(
                    payment.borrowing, payment.money_to_pay, payment.type
                )
                payment.status = Payment.StatusChoices.EXPIRED
                payment.save()
                updates_number += 1
    return {"sessions been updated": updates_number}


@shared_task
def create_fine_payment():
    queryset = overdue_borrowings()
    payments_created = 0
    payments_updated = 0
    if queryset:
        for borrowing in queryset:
            fine_amount = borrowing.fine_days * settings.DAILY_FINE_FEE
            fine_payment = borrowing.payment_set.filter(
                type=Payment.TypeChoices.FINE,
                status=Payment.StatusChoices.PENDING,
            ).first()
            if fine_payment:
                session = stripe.checkout.Session.retrieve(
                    fine_payment.session_id
                )
                if session.expires_at < timezone.now().timestamp():
                    fine_payment.delete()
                    create_stripe_payment(
                        borrowing, fine_amount, Payment.TypeChoices.FINE
                    )
                else:
                    fine_payment.money_to_pay = fine_amount
                    fine_payment.save()
                payments_updated += 1
            else:
                create_stripe_payment(
                    borrowing, fine_amount, Payment.TypeChoices.FINE
                )
                payments_created += 1

    return {
        "payments been updated": payments_updated,
        "payments been created": payments_created,
    }
