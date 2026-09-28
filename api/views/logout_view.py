from drf_spectacular.utils import extend_schema
from rest_framework import request, response, status, views

from api import serializers
from conf.container import get_container
from iam import commands, handlers


class LogoutView(views.APIView):
    """Revoke the session identified by a refresh token."""

    @extend_schema(
        request=serializers.RefreshTokenRequestSerializer,
        responses={status.HTTP_204_NO_CONTENT: None},
        tags=["iam"],
    )
    def post(self, request: request.Request) -> response.Response:
        srz = serializers.RefreshTokenRequestSerializer(data=request.data)
        srz.is_valid(raise_exception=True)

        cmd = commands.LogoutCommand(**srz.validated_data)
        container = get_container()
        handlers.handle_logout_command(cmd=cmd, hasher=container.hmac_hasher)

        return response.Response(status=status.HTTP_204_NO_CONTENT)
