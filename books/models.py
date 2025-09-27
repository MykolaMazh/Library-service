from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator


class Author(models.Model):
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=35)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "HARD", "Hard"
        SOFT = "SOFT", "Soft"

    title = models.CharField(max_length=255)
    author = models.ForeignKey(
        Author, related_name="written_books", on_delete=models.CASCADE
    )
    synopsis = models.TextField()
    cover = models.CharField(
        max_length=4, choices=CoverChoices.choices, default=CoverChoices.HARD
    )
    inventory = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )
    daily_fee = models.DecimalField(
        max_digits=4, decimal_places=2, default=Decimal("0.00")
    )

    def __str__(self):
        return f"{self.title} by {self.author}"
