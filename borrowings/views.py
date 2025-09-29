import datetime

from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.permissions import IsBorrower
from borrowings.serializers import BorrowingSerializer, BorrowingListSerializer


class BorrowingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = [IsBorrower]

    def perform_create(self, serializer):
        borrowing = serializer.save(user=self.request.user)
        borrowing.book.inventory -= 1
        borrowing.book.save()

    def get_serializer_class(self):
        if self.action in ("list", "rertrieve"):
            return BorrowingListSerializer
        return BorrowingSerializer

    def get_queryset(self):
        users = self.request.query_params.get("user_id")
        queryset = (
            Borrowing.objects.all()
            if self.request.user.is_staff
            else Borrowing.objects.filter(user=self.request.user)
        )
        if users:
            users_ids = [int(str_id) for str_id in users.split(",")]
            queryset = Borrowing.objects.filter(user_id__in=users_ids)
        is_active = self.request.query_params.get("is_active")
        if is_active:
            queryset = queryset.filter(actual_return_date__isnull=True)
        return queryset.select_related("book", "user", "book__author")

    @action(detail=True, methods=["post"], url_path="return")
    def return_book(self, request, pk):
        borrowing = get_object_or_404(Borrowing, pk=pk)
        if borrowing:
            book = borrowing.book
            if borrowing.actual_return_date:
                return Response(
                    {
                        "status": f'"{book}" has already been returned on {borrowing.actual_return_date}',
                    }
                )
        return_date = datetime.date.today()
        borrowing.actual_return_date = return_date
        borrowing.book.inventory += 1
        borrowing.save()
        return Response(
            {
                "status": f"The book has been returned at {return_date}",
            }
        )
