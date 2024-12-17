from dj_rest_auth.views import PasswordChangeView
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    post=extend_schema(
        tags=["Autenticación"], description="Cambia la contraseña del user actual."
    )
)
class CustomPasswordChangeView(PasswordChangeView):
    """Cambia el password del v2 actual."""
