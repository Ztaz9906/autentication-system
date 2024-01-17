from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.views import SpectacularAPIView


@extend_schema_view(
    get=extend_schema(
        tags=["Api"], exclude=True, description="Retorna los esquemas del api actual"
    )
)
class CustomSpectacularApiView(SpectacularAPIView):
    """Esquema de OPENAPI 3. El formato puede ser seleccionado mediante
    negociación de contenido."""
