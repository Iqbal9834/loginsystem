from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from src.apis.serializeres import UserSignupSerializer
from src.apis.utils import create_response, safe_view_request_handler
from src.apis.utils.throttels import ResponseStatusCodeThrottle
from src.apis.mixins.serializers_fields import ValidationError


class UserSignupView(GenericAPIView):
    serializer_class = UserSignupSerializer

    @ResponseStatusCodeThrottle(
        status_codes=[status.HTTP_400_BAD_REQUEST],
        throttle_scope="user_signup_fail",
    )
    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.generate_email_verification_token(save=True)
        # user.send_verify_email_mail()
        response_data = user.get_signup_response()
        return Response(
            create_response(True, data=response_data),
            status=status.HTTP_201_CREATED,
        )
