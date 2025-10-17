from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings

from borrowings.models import Borrowing
from notifications.telegram_helper import send_telegram_message
from payments.helpers import create_stripe_payment


@receiver(post_save, sender=Borrowing)
def notify_new_borrowing(sender, instance, created, **kwargs):
    if created:
        message = (
            f"📚 ***New Borrowing Created!***\n\n"
            f"User: {instance.user}\n"
            f"Book: {instance.book.title}\n"
            f"Borrow date: {instance.borrow_date}\n"
            f"Due date: {instance.expected_return_date}"
        )
        send_telegram_message(message)


@receiver(post_save, sender=Borrowing)
def create_payment_session(sender, instance, created, **kwargs):
    if created:
        amount = instance.borrow_days * settings.DAILY_BORROW_FEE
        create_stripe_payment(instance, amount)
