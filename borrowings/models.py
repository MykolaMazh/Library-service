from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from books.models import Book

User = get_user_model()


class Borrowing(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)

    def clean(self):
        if (
            self.expected_return_date < self.borrow_date
            or self.actual_return_date < self.borrow_date
        ):
            raise ValidationError(
                "Return date cannot be earlier than borrow date."
            )
