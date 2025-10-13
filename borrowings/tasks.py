from datetime import date
from django.db.models import Q
from celery import shared_task

from borrowings.models import Borrowing
from notifications.telegram_helper import (
    send_telegram_overdue_message,
    send_telegram_message,
)


@shared_task
def get_overdue_borrowings():
    today = date.today()
    queryset = Borrowing.objects.filter(
        Q(expected_return_date__lte=today) & Q(actual_return_date__isnull=True)
    )
    if queryset:
        for borrowing in queryset:
            send_telegram_overdue_message(borrowing)
    else:
        send_telegram_message("No borrowings overdue today!")

    return queryset
