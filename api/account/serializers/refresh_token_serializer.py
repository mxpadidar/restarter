from rest_framework import serializers


class RefreshTokenRequestSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(write_only=True)
