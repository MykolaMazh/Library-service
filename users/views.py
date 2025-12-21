from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema

from users.serializers import (
    UserCreateSerializer,
    UserRetrieveUpdateSerializer,
)

User = get_user_model()


@extend_schema(
    summary="Register new user",
    description="Register new user using email.",
)
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer


class RetrieveUpdateUserView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserRetrieveUpdateSerializer

    def get_object(self):
        return User.objects.get(pk=self.request.user.pk)


@extend_schema(
    summary="Obtain JWT token",
    description="Obtain access and refresh JWT tokens using "
    "email and password.",
)
class CustomTokenObtainPairView(TokenObtainPairView):
    pass
