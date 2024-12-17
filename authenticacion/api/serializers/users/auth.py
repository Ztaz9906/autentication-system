from rest_framework import serializers
from authenticacion.models.users import Usuario
from ..groups.auth import SerializadorDeGrupoAuth
from ..permissions.read import SerializadorDePermisos

class SerializadorUsuarioAuth(serializers.ModelSerializer):
    """Clase base utilizada en la serialización/deserialización de los usuarios autenticados."""
    groups = SerializadorDeGrupoAuth(many=True)
    user_permissions = SerializadorDePermisos(many=True)
    class Meta:
        model = Usuario
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "groups",
           'user_permissions',
            'customer_id',
            'phone'
        ]
