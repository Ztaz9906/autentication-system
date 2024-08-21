from authenticacion.models import Usuario, Group
from authenticacion.serializers import SerializadorUsuarioLectura, SerializadorDeUsuarioEscritura, SerializadorDeGrupos, SerializadorDeGruposLectura, CustomPasswordResetSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import permissions, viewsets
from django_filters import rest_framework as filters
from dj_rest_auth.views import LoginView, LogoutView, PasswordResetView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

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
        parameters=[OpenApiParameter(name="query", required=False, type=str)],
    ),
)
class VistasDeGrupos(viewsets.ModelViewSet):
    """Lee y actualiza los grupos."""
    queryset = Group.objects.all()
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["name"]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return SerializadorDeGruposLectura
        return SerializadorDeGrupos

@extend_schema_view(
    create=extend_schema(tags=["Administración"],
                         description="Crea un usuario"),
    retrieve=extend_schema(
        tags=["Administración"], description="Devuelve los detalles de un usuario"
    ),
    update=extend_schema(tags=["Administración"],
                         description="Actualiza un usuario"),
    partial_update=extend_schema(
        tags=["Administración"], description="Actualiza un usuario"
    ),
    destroy=extend_schema(tags=["Administración"],
                          description="Destruye un usuario"),
    list=extend_schema(
        tags=["Administración"],
        description="Lista los usuarios",
        parameters=[OpenApiParameter(name="query", required=False, type=str)],
    ),
)
class VistasDeUsuarios(viewsets.ModelViewSet):
    """Lee y actualiza los usuarios."""
    queryset = Usuario.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SerializadorUsuarioLectura
        return SerializadorDeUsuarioEscritura

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
    ...


@extend_schema_view(
    post=extend_schema(
        tags=["Autenticación"],
        request=None,
        description="Confirma el borrado de la sesión del usuario actual",
    ),
    get=extend_schema(
        tags=["Autenticación"],
        request=None,
        responses=None,
        description="Confirma el proceso de borrado de la sesión del usuario actual",
        deprecated=True,
    ),
)
class CustomLogoutView(LogoutView):
    """Borra el token y la sesión asignada al usuario actual."""
    ...


@extend_schema_view(
    post=extend_schema(
        tags=["Autenticación"],
        description="Inicia el proceso de recuperación de contraseña.",
    )
)
class CustomPasswordResetView(PasswordResetView):
    """Comienza el flujo de reseteo de passwords."""

    serializer_class = CustomPasswordResetSerializer


@extend_schema_view(
    post=extend_schema(
        tags=["Autenticación"],
        description="Inicia la sesión para el usuario con su cuenta de google.",
    )
)
class GoogleLogin(SocialLoginView):
    """Clase usada para la autenticacion por google"""
    adapter_class = GoogleOAuth2Adapter
    callback_url = 'http://127.0.0.1:8000/api/google-login'
    client_class = OAuth2Client
