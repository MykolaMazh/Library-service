from django.db import models

from borrowings.models import Borrowing


class Payment(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "pending", "PENDING"
        PAID = "paid", "PAID"
        EXPIRED = "expired", "EXPIRED"

    class TypeChoices(models.TextChoices):
        PAYMENT = "payment", "PAYMENT"
        FINE = "fine", "FINE"

    status = models.CharField(
        max_length=7,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )
    type = models.CharField(
        max_length=7,
        choices=TypeChoices.choices,
        default=TypeChoices.PAYMENT,
    )
    borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE)
    session_url = models.URLField(max_length=1000)
    session_id = models.CharField(max_length=256)
    money_to_pay = models.DecimalField(max_digits=6, decimal_places=2)
