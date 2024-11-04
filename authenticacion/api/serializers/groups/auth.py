from rest_framework import serializers
from authenticacion.models.groups import Group


class SerializadorDeGrupoAuth(serializers.ModelSerializer):
    """Clase encargada de serializar y deserializar los grupos."""
    class Meta:
        model = Group
        fields = ["name"]