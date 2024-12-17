from django.utils.crypto import get_random_string
from django.conf import settings
from authenticacion.utils.exceptions import TokenExpiredError, TokenInvalidError
from authenticacion.models.activation_token import ActivationToken

class ActivationService:
    def __init__(self, email_service, user_service):
        self.email_service = email_service
        self.user_service = user_service

    def create_activation_token(self, user):
        token = get_random_string(64)
        activation_token = ActivationToken.objects.create(
            user=user,
            token=token
        )
        return activation_token.token

    def activate_user(self, token):
        try:
            activation_token = ActivationToken.objects.get(token=token)
            if not activation_token.is_valid:
                raise TokenExpiredError("El token ha expirado")
                
            user = activation_token.user
            user.is_active = True
            user.save()
            
            activation_token.delete()
            return user
            
        except ActivationToken.DoesNotExist:
            raise TokenInvalidError("Token inválido")