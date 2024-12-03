from rest_framework import serializers
from ..permissions.read import SerializadorDePermisos
from authenticacion.models.users import Usuario
from ..groups.read import SerializadorDeGruposLectura


class SerializadorUsuarioLectura(serializers.ModelSerializer):
    """Clase base utilizada en la serialización/deserialización de los usuarios."""
    groups = SerializadorDeGruposLectura(many=True)
    user_permissions = SerializadorDePermisos(many=True)

    class Meta:
        model = Usuario
        fields = [
            "id",
            'is_active',
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "groups",
            "user_permissions",
            'customer_id',
            'phone'
        ]

