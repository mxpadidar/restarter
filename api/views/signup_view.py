from drf_spectacular.utils import extend_schema
from rest_framework import request, response, status, views

from account import commands, handlers
from api import serializers
from conf.container import get_container


class SignupView(views.APIView):
    """Handle authentication-related signup actions."""

    @extend_schema(
        request=serializers.SignupSerializer,
        responses={status.HTTP_201_CREATED: serializers.IDSerializer},
        tags=["account"],
    )
    def post(self, request: request.Request) -> response.Response:
        srz = serializers.SignupSerializer(data=request.data)
        srz.is_valid(raise_exception=True)

        cmd = commands.SignupCommand(**srz.validated_data)

        container = get_container()

        user = handlers.handle_signup_command(
            cmd=cmd,
            role_manager=container.role_manager,
        )

        return response.Response(
            data={"id": user.id},
            status=status.HTTP_201_CREATED,
        )
