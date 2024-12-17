from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer
from authenticacion.models.groups import Group

@extend_schema_serializer(component_name="SerializadorDeGruposEscritura")
class SerializadorDeGruposEscritura(serializers.ModelSerializer):
    """Clase encargada de serializar y deserializar los grupos."""

    class Meta:
        model = Group
        fields = ["id", "name", "permissions"]