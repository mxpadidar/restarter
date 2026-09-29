from rest_framework import serializers

from account.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serialize safe user fields for administrative listings."""

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        model = User
        fields = ("id", "username", "created_at", "deactivated_at")
        read_only_fields = fields
