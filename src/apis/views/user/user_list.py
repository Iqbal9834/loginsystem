from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from src.apis.models import User
from src.apis.permissions import IsAuthenticated, IsAuthorizedDjangoModelPermissions
from src.apis.serializeres.user_list import UserListSerializer
from src.apis.utils import create_response, safe_view_request_handler


class UserListView(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    @safe_view_request_handler()
    def get(self, request, pk=None):
        if pk:
            user = User.objects.filter(id=pk)
            serializer = UserListSerializer(
                user, many=True, context={"request": request}
            )
        else:
            data = list(User.objects.all().exclude(username=request.user))
            for user in data:
                if user.is_superuser == True:
                    data.remove(user)
            serializer = UserListSerializer(
                data, many=True, context={"request": request}
            )

        return Response(
            create_response(True, data=serializer.data), status=status.HTTP_200_OK
        )
