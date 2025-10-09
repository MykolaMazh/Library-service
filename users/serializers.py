from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "password",
        )
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 5,
                "style": {"input_type": "password"},
            }
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


class UserRetrieveUpdateSerializer(serializers.ModelSerializer):
    books_to_return = serializers.SerializerMethodField()

    def get_books_to_return(self, obj):
        return obj.borrowing_set.filter(
            actual_return_date__isnull=True
        ).count()

    class Meta:
        model = get_user_model()
        fields = (
            "password",
            "id",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "books_to_return",
        )
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 5},
            "is_staff": {"read_only": True},
        }

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
        return user
