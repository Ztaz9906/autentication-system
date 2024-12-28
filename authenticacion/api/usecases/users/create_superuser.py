from django.db import transaction
from django.contrib.auth.models import User
from authenticacion.core.services.email.email_service import EmailService
from authenticacion.core.services.activation.activation_service import ActivationService

class CreateSuperUserUseCase:
    """Caso de uso para crear un superusuario inactivo que requiere activación por email."""

    def __init__(self, serializer_class):
        self.serializer_class = serializer_class

    @transaction.atomic
    def execute(self, data):
        # Validar y preparar los datos con el serializer
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        
        # El serializer ya maneja la generación del username y el hasheo del password
        user = serializer.save()
        
        # Establecer permisos de superusuario
        user.is_staff = True
        user.is_superuser = True
        user.save()
        # Crear token de activación
        token = ActivationService.create_activation_token(self,user)

            # Enviar correo de activación
        EmailService.send_superuser_activation_email(user, token)
        
        # Aquí puedes hacer cualquier otra cosa adicional, como enviar un correo de bienvenida, etc.
        return user
