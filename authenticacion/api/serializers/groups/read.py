
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer
from ..permissions.read import SerializadorDePermisos
from authenticacion.models.groups import Group

@extend_schema_serializer(component_name="SerializadorDeGruposLectura")
class SerializadorDeGruposLectura(serializers.ModelSerializer):
    """Clase encargada de serializar y deserializar los grupos."""

    permissions = SerializadorDePermisos(many=True)

    class Meta:
        model = Group
        fields = ["id", "name", "permissions"]
