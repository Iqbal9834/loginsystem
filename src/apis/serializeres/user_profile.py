from rest_framework.serializers import ModelSerializer

from src.apis.models import User


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "uuid",
            "username",
            "first_name",
            "last_name",
            "email",
            "first_name",
            "last_name",
            "mobile_number",
            "address",
            "email_verified",
            "date_joined",
        )
        read_only_fields = (
            "uuid",
            "username",
            "email",
            "mobile_number",
            "date_joined",
            "last_active",
        )