from typing import cast

from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema
from rest_framework import exceptions, permissions, request, response, status, views

from account.dtos import AuthUser
from account.models import SessionGrant
from api.account import serializers
from core.utils import get_current_datetime


class MeView(views.APIView):
    """Return the authenticated user's profile."""

    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        responses={status.HTTP_200_OK: serializers.MeResponseSerializer},
        tags=["account"],
    )
    def get(self, request: request.Request) -> response.Response:
        auth_user = cast(AuthUser, request.user)
        grant = (
            SessionGrant.objects.select_related("user")
            .filter(
                id=auth_user.session_grant_id,
                user_id=auth_user.user_id,
                revoked_at__isnull=True,
                expires_at__gt=get_current_datetime(),
                user__deleted_at__isnull=True,
                user__deactivated_at__isnull=True,
            )
            .first()
        )
        if grant is None:
            raise exceptions.AuthenticationFailed(_("invalid or expired access token"))

        return response.Response(
            data={
                "id": grant.user.id,
                "username": grant.user.username,
                "created_at": grant.user.created_at,
                "last_login": grant.issued_at,
            },
            status=status.HTTP_200_OK,
        )
