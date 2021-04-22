from rest_framework.serializers import ModelSerializer

from src.apis.models import User


class UserListSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "mobile_number",
            "address",
        )