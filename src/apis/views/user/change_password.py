from django.contrib.auth.hashers import check_password
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response

from src.apis.mixins.serializers_fields import PasswordField
from src.apis.mixins.serializers import UpdateOnlySerializer
from src.apis.models import User
from src.apis.permissions import IsAuthenticated, IsAuthorizedDjangoModelPermissions
from src.apis.serializeres.user_profile import UserProfileSerializer
from src.apis.utils import create_response


class UserChangePasswordSerializer(UpdateOnlySerializer):
    curr_password = PasswordField(disable_validate_password=True)
    new_password = PasswordField()

    def validate(self, attrs):
        curr_password = attrs.get("curr_password")
        user = self.instance
        is_password_correct = check_password(curr_password, user.password)

        if not is_password_correct:
            raise ValidationError("Current password is incorrect")
        return attrs

    def update(self, instance, validated_data):
        user: User = instance
        data = self.validated_data
        update_fields = user.set_password(data["new_password"])
        user.save(update_fields=update_fields)
        return user

    def to_representation(self, instance):
        return UserProfileSerializer(instance).data


class UserChangePasswordView(UpdateAPIView):
    permission_classes = (IsAuthenticated, IsAuthorizedDjangoModelPermissions)
    queryset = User.objects.all()
    serializer_class = UserChangePasswordSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            response.data = create_response(
                True,
                data={"message": "Password has been successfully changed"},
            )
            return response
        except ValidationError as e:
            return Response(
                create_response(False, err_name="BAD_REQUEST", err_message=e.detail),
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            print(e)
            return Response(
                create_response(
                    False,
                    err_name="INTERNAL_SERVER_ERROR",
                    err_message="Something went wrong.",
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
