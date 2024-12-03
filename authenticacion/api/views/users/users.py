from rest_framework import viewsets
from rest_framework.decorators import action
from authenticacion.models.users import Usuario
from authenticacion.api.usecases import users as usecases
from drf_spectacular.utils import extend_schema, extend_schema_view,OpenApiExample
from authenticacion.api.serializers.users import read , write
from django_filters import rest_framework as filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from authenticacion.utils.permisions import IsSuperUser
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
    filterset_fields = ["groups", "is_active", "is_superuser"]

    def get_permissions(self):
        """
        Custom permissions for different actions
        """
        if self.action == 'create':
            # Allow anyone to create a user
            return [AllowAny()]
        elif self.action == 'list':
            # Require authentication for listing users
            return [IsAuthenticated()]
        elif self.action == 'destroy':
            # Only superusers can destroy/deactivate users
            return [IsAuthenticated(), IsSuperUser()]
        elif self.action in ['update', 'partial_update']:
            # Only authenticated users can update, with additional checks in update method
            return [IsAuthenticated()]
        elif self.action == 'retrieve':
            # Authenticated users can retrieve user details
            return [IsAuthenticated()]
        
        # Default to no permissions if action is not specified
        return []


    def get_serializer_class(self):
        if self.request.method == 'GET':
            return read.SerializadorUsuarioLectura
        return write.SerializadorDeUsuarioEscritura
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Usuario.objects.all()
        return Usuario.objects.filter(id=self.request.user.id)

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