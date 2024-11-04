from rest_framework import serializers

class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(help_text="El token de actualización que debe deshabilitarse")

    class Meta:
        fields = ['refresh_token']