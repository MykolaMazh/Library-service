from datetime import date, timedelta
from unittest.mock import patch
from typing import Tuple
from decimal import Decimal

import stripe.checkout
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from books.models import Book, Author
from borrowings.models import Borrowing
from borrowings.tasks import get_overdue_borrowings
from payments.models import Payment
from payments.helpers import create_stripe_payment

User = get_user_model()
expected_return_date = date.today() + timedelta(days=5)
REGISTER_URL = "users:register"
BOOK_LIST = "books:book-list"
BOOK_DETAIL = "books:book-detail"
BORROWING_LIST = "borrowings:borrowing-list"
BORROWING_DETAIL = "borrowings:borrowing-detail"
RETURN_URL = "borrowings:borrowing-return-book"
PAYMENTS_LIST = "payments:payment-list"
PAYMENTS_DETAIL = "payments:payment-detail"


def create_book(suffix_inventory: int):
    Author.objects.create(
        first_name=f"Author_book_{suffix_inventory}_name",
        last_name=f"Author_book_{suffix_inventory}_surname",
    )

    return Book.objects.create(
        title=f"Book-{suffix_inventory} title",
        author=Author.objects.last(),
        cover="HARD",
        inventory=suffix_inventory,
        daily_fee=1.15,
        synopsis=f"Book-{suffix_inventory} synopsis",
    )


def _create_user(user: str, is_staff=False):
    return User.objects.create_user(
        email=f"{user}@example.com",
        password="testpass123",
        is_staff=is_staff,
    )


def borrow_book(user, book):
    return Borrowing.objects.create(
        user=user,
        book=book,
        expected_return_date=expected_return_date,
    )


class BooksApiTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def test_only_admin_can_manage_books(self):
        author = Author.objects.create(
            first_name="Author_name", last_name="Author_surname"
        )
        payload = {
            "title": "Book title",
            "author": author.id,
            "cover": "HARD",
            "inventory": 2,
            "daily_fee": 1.15,
            "synopsis": "Book synopsis",
        }
        user = _create_user("user")
        self.client.force_authenticate(user)
        response = self.client.post(reverse(BOOK_LIST), payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Book.objects.count(), 0)

        admin_user = _create_user("admin_user", is_staff=True)
        self.client.force_authenticate(admin_user)
        response = self.client.post(reverse(BOOK_LIST), payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 1)

        self.client.force_authenticate(user)
        book_detail_url = reverse(BOOK_DETAIL, args=[1])
        _requests = (
            self.client.put(book_detail_url),
            self.client.patch(book_detail_url),
            self.client.delete(book_detail_url),
        )
        for response in _requests:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        _requests = (
            self.client.get(book_detail_url),
            self.client.get(BOOK_LIST),
        )
        response = self.client.get(book_detail_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg="non-admin user should has access to get requests",
        )


class UsersApiTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def test_register_user(self):
        payload = {
            "email": "newuser@example.com",
            "password": "newpass123",
        }
        res = self.client.post(reverse(REGISTER_URL), payload)
        self.assertEqual(
            res.status_code,
            status.HTTP_201_CREATED,
            msg="The user should be created with email instead of nickname",
        )
        user_exists = User.objects.filter(email=payload["email"]).exists()
        self.assertTrue(user_exists)


@patch("borrowings.signals.create_stripe_payment")
@patch("borrowings.signals.send_telegram_message")
class BorrowingsApiTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def test_authenticate_to_borrow(self, mock_send, mock_create_payment):
        user1 = _create_user("user1")
        book = create_book(suffix_inventory=1)
        borrow_data = {
            "book": Book.objects.last().id,
            "expected_return_date": expected_return_date,
        }
        response = self.client.post(
            reverse(BORROWING_LIST),
            data=borrow_data,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user1)
        response = self.client.post(
            reverse(BORROWING_LIST),
            data=borrow_data,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Borrowing.objects.last().user,
            user1,
            msg="created Borrowing instance's user is active user.",
        )

    def test_reduce_inventory(self, mock_send, mock_create_payment):
        user1 = _create_user("user1")
        book_inventory = 8
        book = create_book(suffix_inventory=book_inventory)
        borrow_data = {
            "book": Book.objects.last().id,
            "expected_return_date": expected_return_date,
        }
        self.client.force_authenticate(user1)
        self.client.post(
            reverse(BORROWING_LIST),
            data=borrow_data,
        )
        book.refresh_from_db()
        self.assertEqual(book.inventory, book_inventory - 1)

    def test_access_only_own_borrowings(self, mock_send, mock_create_payment):
        book1 = create_book(suffix_inventory=1)
        user1 = _create_user("user1")
        self.client.force_authenticate(user1)
        borrow_data = {
            "book": Book.objects.last().id,
            "expected_return_date": expected_return_date,
        }
        self.client.post(
            reverse(BORROWING_LIST),
            data=borrow_data,
        )

        book2 = create_book(suffix_inventory=2)
        borrow_data.update({"book": Book.objects.last().id})
        user2 = _create_user("user2")
        self.client.force_authenticate(user2)
        self.client.post(reverse(BORROWING_LIST), data=borrow_data),
        self.assertEqual(Borrowing.objects.count(), 2)

        response = self.client.get(reverse(BORROWING_LIST))
        self.assertEqual(
            len(response.data),
            1,
            msg="user has access only to own borrowings list",
        )

        response = self.client.get(
            reverse(BORROWING_DETAIL, args=[Borrowing.objects.first().id])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            msg="user has access only to own borrowing",
        )

    def test_list_with_query_params(self, mock_send, mock_create_payment):
        for _ in range(10, 20):
            create_book(suffix_inventory=_)
        user1 = _create_user("user1")
        for i in range(2):
            borrow_book(user1, Book.objects.order_by("?").first())

        user2 = _create_user("user2")
        self.client.force_authenticate(user2)
        for i in range(2):
            borrow_book(user2, Book.objects.order_by("?").first())
        response = self.client.get(
            reverse(BORROWING_LIST) + "?user_id=" + str(user1.id)
        )
        self.assertEqual(
            len(response.data), 0, msg='users can\'t use filter by "user_id"'
        )

        borrowing = Borrowing.objects.filter(user=user2).last()
        borrowing.actual_return_date = date.today()
        borrowing.save()
        response = self.client.get(
            reverse(BORROWING_LIST) + "?is_active=" + " "
        )
        self.assertEqual(
            len(response.data),
            1,
            msg='is_active displays only not returned books."',
        )

    def test_return_book(self, mock_send, mock_create_payment):
        book = create_book(suffix_inventory=10)
        for i in range(3):
            user = _create_user(f"user{i}")
            self.client.force_authenticate(user)
            self.client.post(
                reverse(BORROWING_LIST),
                data={
                    "book": book.id,
                    "expected_return_date": expected_return_date,
                },
            )

        borrowing = Borrowing.objects.get(user=user)
        self.client.post(reverse(RETURN_URL, args=[borrowing.id]))
        self.assertEqual(Book.objects.get(id=book.id).inventory, 8)

    def test_notify_new_borrowing_signal(self, mock_send, mock_create_payment):
        user = _create_user("user")
        self.client.force_authenticate(user)
        create_book(suffix_inventory=1)
        borrow_book(user, Book.objects.last())

        mock_send.assert_called_once()

        borrowing = Borrowing.objects.last()

        text_from_instance_created = (
            f"📚 ***New Borrowing Created!***\n\n"
            f"User: {borrowing.user}\n"
            f"Book: {borrowing.book.title}\n"
            f"Borrow date: {borrowing.borrow_date}\n"
            f"Due date: {borrowing.expected_return_date}"
        )
        text_from_message_sent = mock_send.call_args[0][0]
        self.assertEqual(text_from_instance_created, text_from_message_sent)

    def test_only_one_unpaid_borrowing(self, mock_send, mock_create_payment):
        user = _create_user("user")
        self.client.force_authenticate(user)
        book = create_book(suffix_inventory=1)
        borrowing = borrow_book(user, Book.objects.last())
        Payment.objects.create(
            borrowing=borrowing,
            money_to_pay=Decimal("10.20"),
            session_id="test_session_id_12854",
            session_url="testt_session_url_455465",
            status="pending",
            type=Payment.TypeChoices.PAYMENT,
        )

        self.assertEqual(Payment.objects.count(), 1)

        borrow_data = {
            "book": book.id,
            "expected_return_date": expected_return_date,
        }
        response = self.client.post(
            reverse(BORROWING_LIST),
            data=borrow_data,
        )
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(response.status_code, 400)

    @patch("borrowings.models.Borrowing.clean", return_value=None)
    @patch("borrowings.tasks.send_telegram_overdue_message")
    def test_notify_daily_overdue_borrowings(
        self,
        mock_send_overdue,
        mock_clean,
        mock_send,
        mock_create_payment,
    ):
        user = _create_user("user")
        self.client.force_authenticate(user)
        create_book(suffix_inventory=1)
        create_book(suffix_inventory=2)

        borrow_book(user, Book.objects.last())
        overdue_borrowing = Borrowing.objects.create(
            user=user,
            book=Book.objects.first(),
            expected_return_date=date.today() - timedelta(days=3),
        )
        overdue_borrowings = get_overdue_borrowings()

        mock_send_overdue.assert_called_with(overdue_borrowing)


@patch("borrowings.signals.send_telegram_message")
class PaymentsApiTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def create_payment(self) -> Tuple[Borrowing, Payment]:
        book = create_book(suffix_inventory=1)
        user1 = _create_user("user1")
        self.client.force_authenticate(user1)
        borrowing = borrow_book(user1, book)
        payment = Payment.objects.first()
        return (borrowing, payment)

    def test_borrowing_creates_payment(self, mock_send):
        borrowing, payment = self.create_payment()
        self.assertEqual(payment.borrowing, borrowing)

    @patch("borrowings.signals.create_stripe_payment")
    def test_borrowing_creates_checkout_session(
        self, mock_create_payment, mock_send
    ):
        borrowing = self.create_payment()[0]
        checkout_session = create_stripe_payment(borrowing, Decimal("10.50"))

        self.assertIsInstance(checkout_session, stripe.checkout.Session)

        self.assertRegex(checkout_session.id, r"^cs_[a-zA-Z0-9_]+$")
        self.assertRegex(
            checkout_session.url, r"^https://checkout\.stripe\.com/.*+"
        )

    # @patch("borrowings.signals.create_stripe_payment")
    def test_only_own_payments_visible(self, mock_send):
        payment = self.create_payment()[1]
        user1 = User.objects.first()
        staff_user = _create_user("staff_user", is_staff=True)

        for user in user1, staff_user:
            self.client.force_authenticate(user)
            response = self.client.get(reverse(PAYMENTS_LIST))
            self.assertEqual(len(response.data), 1)
            response = self.client.get(
                reverse(PAYMENTS_DETAIL, args=[payment.id])
            )
            self.assertEqual(response.status_code, 200)

        user2 = _create_user("user2")
        self.client.force_authenticate(user2)
        response = self.client.get(reverse(PAYMENTS_LIST))
        self.assertEqual(len(response.data), 0)
        response = self.client.get(reverse(PAYMENTS_DETAIL, args=[payment.id]))
        self.assertEqual(response.status_code, 404)
