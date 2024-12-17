from dj_rest_auth.views import LogoutView
from authenticacion.api.serializers.auth import LogoutSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    post=extend_schema(
        tags=["Autenticación"],
        request=LogoutSerializer,
        description="Confirma el borrado de la sesión del usuario actual",
    ),
    get=extend_schema(exclude=True),
)
class CustomLogoutView(LogoutView):
    """Borra el token y la sesión asignada al usuario actual."""

    serializer_class = LogoutSerializer
