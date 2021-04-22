from rest_framework.serializers import ModelSerializer

from src.apis.models import User
from src.apis.mixins.serializers_fields import PasswordField, ValidationError


class UserSignupSerializer(ModelSerializer):
    password = PasswordField()

    class Meta:
        model = User
        fields = (
            "email",
            "mobile_number",
            "password",
            "first_name",
            "last_name",
            "address"
        )

    def create(self, validated_data):
        user = User.create_app_user(
            validated_data["email"],
            validated_data["password"],
            validated_data["first_name"],
            validated_data["last_name"],
            validated_data["address"],
            mobile_number=validated_data.get("mobile_number"),
        )
        if user is None:
            raise ValidationError("User with this email address already exists")
        return user
