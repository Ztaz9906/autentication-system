from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from django_filters import rest_framework as filters
from .models import Pedido, Producto, UnidadMedida
from .serializers import (
    PedidoSerializer,
    PedidoSerializerLectura,
    ProductoSerializer,
    ProductoSerializerLectura, UnidadMedidaSerializer,
)


@extend_schema_view(
    create=extend_schema(tags=["Pedidos"], description="Crea un pedido"),
    retrieve=extend_schema(tags=["Pedidos"], description="Devuelve los detalles de un pedido"),
    update=extend_schema(tags=["Pedidos"], description="Actualiza un pedido"),
    partial_update=extend_schema(tags=["Pedidos"], description="Actualiza parcialmente un pedido"),
    destroy=extend_schema(tags=["Pedidos"], description="Destruye un pedido"),
    list=extend_schema(
        tags=["Pedidos"],
        description="Lista los pedidos",
        parameters=[OpenApiParameter(name="query", required=False, type=str)],
    ),
)
class PedidoViewSet(viewsets.ModelViewSet):
    """Lee y actualiza los pedidos."""
    queryset = Pedido.objects.all()
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["user__username", "created_at"]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return PedidoSerializerLectura
        return PedidoSerializer


@extend_schema_view(
    create=extend_schema(tags=["Productos"], description="Crea un producto"),
    retrieve=extend_schema(tags=["Productos"], description="Devuelve los detalles de un producto"),
    update=extend_schema(tags=["Productos"], description="Actualiza un producto"),
    partial_update=extend_schema(tags=["Productos"], description="Actualiza parcialmente un producto"),
    destroy=extend_schema(tags=["Productos"], description="Destruye un producto"),
    list=extend_schema(
        tags=["Productos"],
        description="Lista los productos",
        parameters=[OpenApiParameter(name="query", required=False, type=str)],
    ),
)
class ProductoViewSet(viewsets.ModelViewSet):
    """Lee y actualiza los productos."""
    queryset = Producto.objects.all()
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["name", "price", "stock"]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return ProductoSerializerLectura
        return ProductoSerializer


@extend_schema_view(
    create=extend_schema(tags=["Nomeclador"], description="Crea una unidad de medida"),
    retrieve=extend_schema(tags=["Nomeclador"], description="Devuelve los detalles de una unidad de medida"),
    update=extend_schema(tags=["Nomeclador"], description="Actualiza una unidad de medida"),
    partial_update=extend_schema(tags=["Nomeclador"], description="Actualiza parcialmente una unidad de medida"),
    destroy=extend_schema(tags=["Nomeclador"], description="Destruye una unidad de medida"),
    list=extend_schema(
        tags=["Nomeclador"],
        description="Lista las unidades de medida",
        parameters=[OpenApiParameter(name="query", required=False, type=str)],
    ),
)
class UnidadMedidaViewSet(viewsets.ModelViewSet):
    """Lee y actualiza las unidades de medida."""
    queryset = UnidadMedida.objects.all()
    serializer_class = UnidadMedidaSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["name"]
    permission_classes = [permissions.IsAuthenticated]