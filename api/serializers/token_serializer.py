from rest_framework import serializers


class TokenPairResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    token_type = serializers.CharField()
    expires_at = serializers.DateTimeField()
