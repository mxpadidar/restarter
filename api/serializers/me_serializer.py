from rest_framework import serializers


class MeResponseSerializer(serializers.Serializer):
    """Describe the authenticated API principal."""

    id = serializers.UUIDField(read_only=True)
    roles = serializers.ListField(child=serializers.CharField(), read_only=True)
