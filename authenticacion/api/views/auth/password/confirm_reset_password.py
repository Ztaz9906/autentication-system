from dj_rest_auth.views import PasswordResetConfirmView
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    post=extend_schema(
        tags=["Autenticación"],
        description="Termina el proceso de recuperación de contraseñas.",
    )
)
class CustomPasswordResetConfirmView(
 PasswordResetConfirmView
):
    """Termina el flujo de reseteo de passwords."""
