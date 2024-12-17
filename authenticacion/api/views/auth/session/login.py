from dj_rest_auth.views import LoginView
from authenticacion.api.serializers.auth import CustomLoginSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
        post=extend_schema(
            tags=["Autenticación"],
            description=f"Inicia la sesión para el usuario",
        ),
    )
class CustomLoginView(LoginView):
    f"""Comprueba las credenciales y retorna el token apropiado si
    las credenciales son válidas, además habilita una sesión para el usuario.
    """
    serializer_class = CustomLoginSerializer
