from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from books.models import Book, Author
from borrowings.models import Borrowing

User = get_user_model()
REGISTER_URL = "users:register"
BOOK_LIST = "books:book-list"
BOOK_DETAIL = "books:book-detail"
BORROWING_LIST = "borrowings:borrowing-list"
BORROWING_DETAIL = "borrowings:borrowing-detail"


def create_book(id_inventory: int):
    Author.objects.create(
        first_name=f"Author_book_{id_inventory}_name",
        last_name=f"Author_book_{id_inventory}_surname",
    )

    return Book.objects.create(
        title=f"Book-{id_inventory} title",
        author=Author.objects.last(),
        cover="HARD",
        inventory=id_inventory,
        daily_fee=1.15,
        synopsis=f"Book-{id_inventory} synopsis",
    )


def _create_user(user: str, is_staff=False):
    return User.objects.create_user(
        email=f"{user}@example.com",
        password="testpass123",
        is_staff=is_staff,
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


class BorrowingApiTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def test_authenticate_to_borrow(self):
        user1 = _create_user("user1")
        book = create_book(1)
        borrow_data = {
            "book": Book.objects.last().id,
            "expected_return_date": "2026-10-02",
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

    def test_reduce_inventory(self):
        user1 = _create_user("user1")
        book_inventory = 8
        book = create_book(book_inventory)
        borrow_data = {
            "book": Book.objects.last().id,
            "expected_return_date": "2026-10-02",
        }
        self.client.force_authenticate(user1)
        response = self.client.post(
            reverse(BORROWING_LIST),
            data=borrow_data,
        )
        book.refresh_from_db()
        self.assertEqual(book.inventory, book_inventory - 1)

    def test_access_only_own_borrowings(self):
        book1 = create_book(1)
        user1 = _create_user("user1")
        self.client.force_authenticate(user1)
        borrow_data = {
            "book": Book.objects.last().id,
            "expected_return_date": "2026-10-02",
        }
        self.client.post(
            reverse(BORROWING_LIST),
            data=borrow_data,
        )

        book2 = create_book(2)
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
