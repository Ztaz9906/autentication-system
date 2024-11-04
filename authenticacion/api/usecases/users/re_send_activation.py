from rest_framework import status
from rest_framework.response import Response
from authenticacion.core.services.activation.activation_service import ActivationService
from authenticacion.models.users import Usuario
from authenticacion.core.services.email.email_service import EmailService

class ResendActivationUseCase:
    """Caso de uso para activar usuarios."""
    
    def execute(self, email):
        if not email:
            return Response(
                {"error": "Email no proporcionado"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = Usuario.objects.get(email=email)

            if user.is_active:
                return Response(
                    {"error": "Este usuario ya está activado."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Crear nuevo token
            token = ActivationService.create_activation_token(user)
            
            # Enviar email
            EmailService.send_activation_email(user, token)

            return Response(
                {"message": "Correo de activación reenviado"}, 
                status=status.HTTP_200_OK
            )

        except Usuario.DoesNotExist:
            return Response(
                {"error": "Usuario no encontrado"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
