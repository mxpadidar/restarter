from rest_framework import serializers


class RotateRefreshTokenRequestSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(write_only=True)
