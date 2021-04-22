from rest_framework.generics import RetrieveUpdateAPIView

from src.apis.models import User
from src.apis.permissions import IsAuthenticated, IsAuthorizedDjangoModelPermissions
from src.apis.serializeres.user_profile import UserProfileSerializer
from src.apis.utils import create_response, safe_view_request_handler


class UserProfileView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, IsAuthorizedDjangoModelPermissions)
    queryset = User.objects
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

    @safe_view_request_handler()
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        response.data = create_response(True, data=response.data)
        return response

    @safe_view_request_handler()
    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        response = super().update(request, *args, **kwargs)
        response.data = create_response(True, data=response.data)
        return response
