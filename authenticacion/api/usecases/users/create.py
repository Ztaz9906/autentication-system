from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from authenticacion.core.services.email.email_service import EmailService
from authenticacion.core.services.activation.activation_service import ActivationService
from authenticacion.core.services.stripe.stripe_service import StripeService
from authenticacion.utils.exceptions import StripeError


class CreateUsuario(mixins.CreateModelMixin):
    """Clase encargada de la creación de usuarios."""

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Crear el usuario en Django (inicialmente inactivo)
        user = serializer.save()

        try:
            # Crear el cliente en Stripe
            stripe_customer = StripeService.create_customer(user)
            print('En el create llega el id',stripe_customer)
            # Guardar el ID del cliente de Stripe en el modelo de usuario
            user.customer_id = stripe_customer
            user.save()

            # Crear token de activación
            token = ActivationService.create_activation_token(self,user)

            # Enviar correo de activación
            EmailService.send_activation_email(user, token)
        except StripeError as e:
            # Si hay un error al crear el cliente en Stripe, eliminar el usuario de Django
            user.delete()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Si hay un error al enviar el correo, eliminar el usuario de Django y el cliente de Stripe
            StripeService.delete_customer(user.customer_id)
            user.delete()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)