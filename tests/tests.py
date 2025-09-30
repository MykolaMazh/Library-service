from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from books.models import Book, Author

User = get_user_model()
REGISTER_URL = "users:register"
BOOK_LIST = "books:book-list"
BOOK_DETAIL = "books:book-detail"


def create_book(self, _id):
    Author.objects.create(
        first_name=f"Author_book_{_id}_name",
        last_name=f"Author_book_{_id}_surname",
    )

    Book.objects.create(
        title=f"Book-{id} title",
        author=Author.objects.last(),
        cover="HARD",
        inventory=_id,
        daily_fee=1.15,
        synopsis=f"Book-{id} synopsis",
    )


def create_user(self, user: str, is_staff=False):
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
            "synopsis": f"Book-{id} synopsis",
        }
        user = create_user(self, "user")
        self.client.force_authenticate(user)
        response = self.client.post(reverse(BOOK_LIST), payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Book.objects.count(), 0)

        admin_user = create_user(self, "admin_user", is_staff=True)
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
