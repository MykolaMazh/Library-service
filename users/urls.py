from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import (
    CreateUserView,
    RetrieveUpdateUserView,
    CustomTokenObtainPairView,
)

urlpatterns = [
    path(
        "token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", CreateUserView.as_view(), name="register"),
    path("me/", RetrieveUpdateUserView.as_view(), name="me"),
]


app_name = "users"
