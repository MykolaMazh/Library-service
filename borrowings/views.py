import datetime
from typing import List

from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    OpenApiResponse,
)

from borrowings.models import Borrowing
from borrowings.permissions import IsBorrower
from borrowings.serializers import BorrowingSerializer, BorrowingListSerializer


null = None


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
        if self.action in ("list", "retrieve"):
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
            queryset = queryset.filter(user_id__in=users_ids)
        is_active = self.request.query_params.get("is_active")
        if is_active:
            queryset = queryset.filter(actual_return_date__isnull=True)
        return queryset.select_related("book", "user", "book__author")

    @extend_schema(
        summary="Return a borrowed book.",
        description="Return borrowed book with provided id.",
        request=None,
    )
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
        with transaction.atomic():
            borrowing.actual_return_date = return_date
            borrowing.save()
            book.inventory += 1
            book.save()

        return Response(
            {
                "status": f'Thank You. "{book}" has been returned on {return_date}.',
            }
        )

    @extend_schema(
        summary="Borrow a book.",
        description="Create new Borrowing instance. Authentication required. After Borrowing instance has been created"
        " notification is sent to Telegram chat.",
        examples=[
            OpenApiExample(
                name="Example",
                description='"book" is the  Book instance\'s id',
                value={"book": 3, "expected_return_date": "2025-10-05"},
            )
        ],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Get list of borrowings",
        description="User can get own borrowings list and filter by ''is_active''(is a book returned or not)."
        "Admin user can get all users' borrowings and filter by ''user_id''",
        # Define a path parameter named "id"
        parameters=[
            OpenApiParameter(
                name="user_id",
                description="The user’s ID used to retrieve their borrowings.",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="is_active",
                description="Parameter to get only active borrowings(borrowings of books that haven’t been returned yet). Should be ANY STRING",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=List[OpenApiTypes.OBJECT],
                description="Responses",
                examples=[
                    OpenApiExample(
                        name="Response body for non-admin user",
                        value=[
                            {
                                "id": 18,
                                "book": "Call of the Camino22 by Suzanne Redfearn",
                                "borrow_date": "2025-10-05",
                                "expected_return_date": "2025-10-09",
                                "actual_return_date": null,
                            },
                            {
                                "id": 19,
                                "book": "Call of the Camino23 by Suzanne Redfearn",
                                "borrow_date": "2025-10-05",
                                "expected_return_date": "2025-10-09",
                                "actual_return_date": "2025-10-05",
                            },
                        ],
                    ),
                    OpenApiExample(
                        name="Response body for admin user",
                        value=[
                            {
                                "id": 18,
                                "book": "Call of the Camino22 by Suzanne Redfearn",
                                "borrow_date": "2025-10-05",
                                "expected_return_date": "2025-10-09",
                                "actual_return_date": null,
                                "user": "user1@gmail.com",
                                "user_id": 1,
                            },
                            {
                                "id": 19,
                                "book": "Call of the Camino23 by Suzanne Redfearn",
                                "borrow_date": "2025-10-05",
                                "expected_return_date": "2025-10-09",
                                "actual_return_date": "2025-10-05",
                                "user": "user1@gmail.com",
                                "user_id": 1,
                            },
                            {
                                "id": 20,
                                "book": "King of Ashes by A.C. Colby",
                                "borrow_date": "2025-10-05",
                                "expected_return_date": "2025-10-09",
                                "actual_return_date": null,
                                "user": "user3@gmail.com",
                                "user_id": 3,
                            },
                        ],
                    ),
                ],
            )
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
