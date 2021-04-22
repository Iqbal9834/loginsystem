from django.conf import settings
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.serializers import ValidationError


from src.apis.mixins.serializers_fields import MobileNumberField
from src.apis.mixins.serializers import ViewRequestSerializer

from src.apis.models import User
from src.apis.utils import create_response
from src.apis.utils.throttels import ResponseStatusCodeThrottle
from src.apis.service import BaseOtpNotification


class SendLoginOTPSerializer(ViewRequestSerializer):
    mobile = MobileNumberField()


class SendLoginOTPView(GenericAPIView):
    serializer_class = SendLoginOTPSerializer

    @ResponseStatusCodeThrottle(
        status_codes=[status.HTTP_200_OK], throttle_scope="login_otp_success"
    )
    def post(self, request):
        try:
            data = request.data
            serializer: SendLoginOTPSerializer = self.get_serializer(data=data)
            try:
                serializer.is_valid(raise_exception=True)
            except ValidationError as e:
                return Response(
                    create_response(
                        False, err_name="BAD_REQUEST", err_message=e.detail
                    ),
                    status=status.HTTP_400_BAD_REQUEST,
                )
            mobile_number = serializer.validated_data.get("mobile")
            print(f"Trying to fetch user for mobile {mobile_number}")
            user = User.get_user_for_mobile_number(mobile_number, is_active=True)
            if user is None:
                print(f"Not found any user for mobile {mobile_number}")
                return Response(
                    create_response(True, data={"message": "otp sent to mobile"}),
                    status=status.HTTP_200_OK,
                )
            otp_sender = BaseOtpNotification(context=None)
            otp_sender.send_verfication_code(user)

            print(
                f"Login Otp Notification sent successfully to mobile"
                f" {mobile_number}"
            )
            return Response(
                create_response(True, data={"message": "otp sent to mobile"}),
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print(e)
            return Response(
                create_response(
                    False,
                    err_name="BAD REQUEST",
                    err_message="Failed to sent " "otp",
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )
