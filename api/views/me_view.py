from typing import cast

from drf_spectacular.utils import extend_schema
from rest_framework import permissions, request, response, status, views

from api import serializers
from iam.dtos import AuthUser


class MeView(views.APIView):
    """Return the authenticated API principal."""

    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        responses={status.HTTP_200_OK: serializers.MeResponseSerializer},
        tags=["iam"],
    )
    def get(self, request: request.Request) -> response.Response:
        auth_user = cast(AuthUser, request.user)

        return response.Response(
            data={
                "id": auth_user.user_id,
                "roles": sorted(role.value for role in auth_user.roles),
            },
            status=status.HTTP_200_OK,
        )
