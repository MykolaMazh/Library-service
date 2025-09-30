from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from users.serializers import (
    UserCreateSerializer,
    UserRetrieveUpdateSerializer,
)

User = get_user_model()


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer


class RetrieveUpdateUserView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserRetrieveUpdateSerializer

    def get_object(self):
        return User.objects.get(pk=self.request.user.pk)
