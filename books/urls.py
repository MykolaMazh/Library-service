from django.urls import path
from rest_framework.routers import DefaultRouter

from books.views import BookViewSet, AuthorViewSet

router = DefaultRouter()
router.register("books", BookViewSet)
router.register("authors", AuthorViewSet)
urlpatterns = router.urls


app_name = "books"
