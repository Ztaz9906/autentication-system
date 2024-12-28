from rest_framework import status
from rest_framework.exceptions import ValidationError, APIException
from django.db import transaction
from authenticacion.core.services.email.email_service import EmailService
from authenticacion.core.services.activation.activation_service import ActivationService
from rest_framework.response import Response


class CreateSuperUserUseCase:
    """Caso de uso para crear un superusuario inactivo que requiere activación por email."""

    @transaction.atomic
    def execute(self, data, serializer_class):
        try:
            # Validar y preparar los datos con el serializer
            serializer = serializer_class(data=data)
            serializer.is_valid(raise_exception=True)

            # Crear el usuario
            user = serializer.save()
            user.is_staff = True
            user.is_superuser = True
            user.save()

            
            # Crear token de activación y enviar correo
            token = ActivationService.create_activation_token(self,user)
           
            EmailService.send_superuser_activation_email(user, token)

            # Retornar respuesta exitosa
            return Response(
                {
                    "message": "Superusuario creado. Por favor revisa tu email para activarlo.",
                    "email": user.email,
                },
                status=status.HTTP_201_CREATED,
            )

        except ValidationError as ve:
            # Capturar errores de validación del serializer
            return Response(
                {"detail": ve.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            # Manejar errores generales
            raise APIException(f"Error al procesar la solicitud: {str(e)}")
