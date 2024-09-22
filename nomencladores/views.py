from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Provincia, Municipio
from .serializers import ProvinciaSerializer, MunicipioSerializer
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    list=extend_schema(
        tags=["Provicias"],
        description="Lista todas las provicias y sus municipios",
    ),
    retrieve=extend_schema(
        tags=["Provicias"],
        description="Obtiene los detalles de una provicia específica"
    ),
    municipios=extend_schema(
        tags=["Provicias"],
        description="Obtiene los municipios de una provicia específica"
    ),
    destroy=extend_schema(exclude=True),
    create=extend_schema(exclude=True),
    update=extend_schema(exclude=True),
    partial_update=extend_schema(exclude=True),
)
class ProvinciaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Provincia.objects.all()
    serializer_class = ProvinciaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["name"]
    http_method_names = ['get', 'head', 'options']

    @action(detail=True, methods=['get'])
    def municipios(self, request, pk=None):
        provincia = self.get_object()
        municipios = Municipio.objects.filter(provincia=provincia)
        serializer = MunicipioSerializer(municipios, many=True)
        return Response(serializer.data)
