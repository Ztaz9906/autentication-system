from dj_rest_auth.views import PasswordResetView
from drf_spectacular.utils import extend_schema, extend_schema_view
from authenticacion.api.serializers.auth import CustomPasswordResetSerializer

@extend_schema_view(
    post=extend_schema(
        tags=["Autenticación"],
        description="Inicia el proceso de recuperación de contraseña.",
    )
)
class CustomPasswordResetView(PasswordResetView):
    """Comienza el flujo de reseteo de passwords."""

    serializer_class = CustomPasswordResetSerializer