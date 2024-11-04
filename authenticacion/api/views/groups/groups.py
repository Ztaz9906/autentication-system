from rest_framework import viewsets,permissions
from authenticacion.models.groups import Group
from authenticacion.api.usecases import groups as usecases
from drf_spectacular.utils import extend_schema, extend_schema_view
from authenticacion.api.serializers.groups import read , write
from django_filters import rest_framework as filters

from authenticacion.api.serializers.users.auth import SerializadorDeGrupoAuth


@extend_schema_view(
    create=extend_schema(tags=["Administración"], description="Crea un grupo"),
    retrieve=extend_schema(
        tags=["Administración"], description="Devuelve los detalles de un grupo"
    ),
    update=extend_schema(tags=["Administración"],
                         description="Actualiza un grupo"),
    partial_update=extend_schema(
        tags=["Administración"], description="Actualiza un grupo"
    ),
    destroy=extend_schema(tags=["Administración"],
                          description="Destruye un grupo"),
    list=extend_schema(
        tags=["Administración"],
        description="Lista los grupos",
    ),
)
class VistasDeGrupos(
    usecases.CreateGrupo,
    usecases.DeleteGrupo,
    usecases.DetailGrupo,
    usecases.ListGrupo,
    usecases.UpdateGrupo,
    viewsets.GenericViewSet,):
    """Lee y actualiza los grupos."""
    queryset = Group.objects.all()
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["name"]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return read.SerializadorDeGruposLectura
        return write.SerializadorDeGruposEscritura
