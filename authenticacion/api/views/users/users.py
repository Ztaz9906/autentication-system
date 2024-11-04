from rest_framework import viewsets
from rest_framework.decorators import action
from authenticacion.models.users import Usuario
from authenticacion.api.usecases import users as usecases
from drf_spectacular.utils import extend_schema, extend_schema_view,OpenApiExample
from authenticacion.api.serializers.users import read , write
from django_filters import rest_framework as filters

@extend_schema_view(
    create=extend_schema(tags=["Usuarios"],
                         description="Crea un usuario"),
    retrieve=extend_schema(
        tags=["Usuarios"], description="Devuelve los detalles de un usuario"
    ),
    update=extend_schema(tags=["Usuarios"],
                         description="Actualiza un usuario"),
    partial_update=extend_schema(
        tags=["Usuarios"], description="Actualiza un usuario"
    ),
    destroy=extend_schema(tags=["Usuarios"],
                          description="Destruye un usuario"),
    list=extend_schema(
        tags=["Usuarios"],
        description="Lista los usuarios",
    ),
)
class VistasDeUsuarios(
    usecases.CreateUsuario,
    usecases.DetailUsuario,
    usecases.UpdateUsuario,
    usecases.DeleteUsuario,
    usecases.ListUsuario,
    viewsets.GenericViewSet,
):
    """Vista principal de usuarios."""
    queryset = Usuario.objects.all()
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["groups"]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return read.SerializadorUsuarioLectura
        return write.SerializadorDeUsuarioEscritura
    

    @extend_schema(
        tags=["Activación"],
        description="Activa un usuario a partir del token de activación",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'token': {
                        'type': 'string',
                        'description': 'Token de activación enviado por correo'
                    }
                },
                'required': ['token']
            }
        },
        responses={
            200: OpenApiExample(
                'Activación exitosa',
                value={"message": "Usuario activado correctamente"},
            ),
            400: OpenApiExample(
                'Error en activación',
                value={"error": "Token inválido o expirado"},
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='activar')
    def activar_usuario(self, request):
        """Endpoint para activar usuario."""
        use_case = usecases.ActivateUsuarioUseCase()
        return use_case.execute(request.data.get('token'))
    @extend_schema(
        tags=["Activación"],
        description="Reenvía el correo de activación si no llegó o el token expiró.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'email': {
                        'type': 'string',
                        'description': 'Email del usuario que necesita reactivar su cuenta'
                    }
                },
                'required': ['email']
            }
        },
        responses={
            200: OpenApiExample(
                'Reenvío exitoso',
                value={"message": "Correo de activación reenviado"},
            ),
            400: OpenApiExample(
                'Error',
                value={"error": "Usuario no encontrado o ya activado"},
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='reenviar-activacion')
    def reenviar_activacion(self, request):
        """Endpoint para reenviar activación."""
        use_case = usecases.ResendActivationUseCase()
        return use_case.execute(request.data.get('email'))