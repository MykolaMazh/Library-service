from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from books.urls import app_name
from users.views import CreateUserView

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),
    path("register", CreateUserView.as_view(), name="register"),
]


app_name = "users"
