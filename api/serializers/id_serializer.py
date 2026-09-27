"""Serializers for responses that contain a resource identifier."""

from rest_framework import serializers


class IDSerializer(serializers.Serializer):
    """Describe a response containing a resource ID."""

    id = serializers.UUIDField(read_only=True)
