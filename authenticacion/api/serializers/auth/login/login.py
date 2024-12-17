from rest_framework import serializers
from django.contrib.auth import get_user_model

class CustomLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')

        if not (username or email):
            msg = 'Debe proporcionar "username" o "email".'
            raise serializers.ValidationError(msg, code='authorization')

        if not password:
            msg = 'Debe proporcionar "password".'
            raise serializers.ValidationError(msg, code='authorization')

        user = None
        user_model = get_user_model()

        if username:
            try:
                user = user_model.objects.get(username=username)
            except user_model.DoesNotExist:
                pass

        if not user and email:
            try:
                user = user_model.objects.get(email=email)
            except user_model.DoesNotExist:
                pass

        if user and user.check_password(password):
            attrs['user'] = user
            return attrs

        msg = 'No se puede iniciar sesión con las credenciales proporcionadas.'
        raise serializers.ValidationError(msg, code='authorization')
