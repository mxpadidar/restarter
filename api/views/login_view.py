from drf_spectacular.utils import extend_schema
from rest_framework import request, response, status, views

from api import serializers
from conf.config import get_config
from conf.container import get_container
from iam import commands, handlers


class LoginView(views.APIView):
    """Authenticate a user and issue access and refresh tokens."""

    @extend_schema(
        request=serializers.LoginRequestSerializer,
        responses={status.HTTP_200_OK: serializers.TokenPairResponseSerializer},
        tags=["iam"],
    )
    def post(self, request: request.Request) -> response.Response:
        srz = serializers.LoginRequestSerializer(data=request.data)
        srz.is_valid(raise_exception=True)

        container = get_container()

        config = get_config()

        cmd = commands.LoginCommand(
            **srz.validated_data,
            access_token_ttl=config.access_token_ttl,
            refresh_token_ttl=config.refresh_token_ttl,
            refresh_token_size=config.refresh_token_size,
            ip_address=request.META.get("REMOTE_ADDR"),
        )

        result = handlers.handle_login_command(
            cmd=cmd,
            hasher=container.hmac_hasher,
            jwt_service=container.jwt_service,
        )

        return response.Response(
            data={
                "access_token": result.access_token,
                "refresh_token": result.refresh_token,
                "token_type": "Bearer",
                "expires_at": result.expires_at,
            },
            status=status.HTTP_200_OK,
        )
