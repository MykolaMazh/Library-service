from rest_framework import mixins, viewsets

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer, BorrowingListSerializer


class BorrowingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer

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
        queryset = Borrowing.objects.all()
        if users:
            users_ids = [int(str_id) for str_id in users.split(",")]
            queryset = Borrowing.objects.filter(user_id__in=users_ids)
        return queryset
