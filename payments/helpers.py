import os
from typing import Union
from decimal import Decimal

import stripe
from django.db import transaction
from django.conf import settings
from dotenv import load_dotenv

from borrowings.models import Borrowing
from payments.models import Payment

load_dotenv()

domain = (
    "http://127.0.0.1:8000"
    if settings.DEBUG
    else os.getenv("STRIPE_PAYMENT_URL_DOMAIN")
)
success_url = domain + "/api/payments/success"
cancel_url = domain + "/api/payments/cancel"

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_payment(borrowing: Borrowing, amount: Union[int, Decimal]):
    try:
        with transaction.atomic():
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
                            "unit_amount": int(amount * 100),
                        },
                        "quantity": 1,
                    }
                ],
                success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=cancel_url,
            )

            Payment.objects.create(
                borrowing=borrowing,
                money_to_pay=amount,
                session_id=checkout_session.id,
                session_url=checkout_session.url,
                status=Payment.StatusChoices.PENDING,
                type=Payment.TypeChoices.PAYMENT,
            )

    except Exception as e:
        raise RuntimeError(f"Payment creation failed: {e}")

    return checkout_session
