from rest_framework import status
from rest_framework.response import Response
from authenticacion.core.services.activation.activation_service import ActivationService
from authenticacion.utils.exceptions import TokenExpiredError, TokenInvalidError

class ActivateUsuarioUseCase:
    """Caso de uso para activar usuarios."""
    
    def execute(self, token):
        if not token:
            return Response({"error": "Token no proporcionado"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Activar el usuario
            ActivationService.activate_user(self,token)
            
            return Response(
                {"message": "Usuario activado correctamente"}, 
                status=status.HTTP_200_OK
            )
            
        except ValueError as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except TokenInvalidError:
            return Response(
                {"error": "El token inválido"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except TokenExpiredError:
            return Response(
                {"error": "El token ha expirado"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
