
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer
from django.contrib.auth.models import Permission

@extend_schema_serializer(component_name="SerializadorDePermisos")
class SerializadorDePermisos(serializers.ModelSerializer):
    """Clase encargada de serializar y deserializar los permisos."""

    class Meta:
        model = Permission
        fields = ("id", "name", "codename")