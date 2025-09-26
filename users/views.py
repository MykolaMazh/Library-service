from rest_framework import generics

from users.serializers import UserCreateSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
