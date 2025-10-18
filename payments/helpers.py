from typing import Union
from decimal import Decimal

import stripe
from django.db import transaction

from borrowings.models import Borrowing
from payments.models import Payment


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
                success_url="https://football.ua/ukraine/565295-ukrajina-z-drugoji-sprobi-obigrala-azerbajjdzhan.html",
                cancel_url="https://football.ua/worldcup/562778-ukrajina-postupilas-franciji-na-starti-vidboru-do-chs-2026.html",
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
