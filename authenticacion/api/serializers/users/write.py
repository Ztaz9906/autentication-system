
from rest_framework import serializers
from authenticacion.models.users import Usuario
import string
import random


class SerializadorDeUsuarioEscritura(serializers.ModelSerializer):
    """Clase encargada de serializar y deserializar los usuarios."""

    password = serializers.CharField(write_only=True)

    def generate_unique_username(self):
        """Genera un nombre de usuario aleatorio y único."""
        while True:
            # Generar un nombre de usuario aleatorio con letras y números
            username = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

            # Comprobar si ya existe un usuario con este nombre
            if not Usuario.objects.filter(username=username).exists():
                return username

    def create(self, validated_data):
        # Generar un nombre de usuario único
        validated_data['username'] = self.generate_unique_username()

        # Crear el usuario
        user = super().create(validated_data)
        user.set_password(validated_data['password'])  # Guardar la contraseña
        user.save()
        return user

    class Meta:
        model = Usuario
        fields = [
            "email",
            'password',
            "first_name",
            "last_name",
            'phone',
            "groups",
            "user_permissions",
        ]
