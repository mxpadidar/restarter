from rest_framework import serializers


class MeResponseSerializer(serializers.Serializer):
    """Describe the authenticated user's profile."""

    id = serializers.UUIDField(read_only=True)
    username = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
