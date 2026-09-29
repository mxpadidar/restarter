from drf_spectacular.utils import extend_schema
from rest_framework import generics

from account.models import User
from account.perms import UserPerm
from api.account.serializers import UserSerializer
from api.perms import has_perms


@extend_schema(tags=["account"])
class UserListView(generics.ListAPIView):
    """List non-deleted users for authorized administrators."""

    permission_classes = has_perms(UserPerm.READ)
    serializer_class = UserSerializer
    queryset = User.objects.filter(deleted_at__isnull=True)
