from rest_framework import status
from rest_framework.response import Response
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from drf_spectacular.utils import extend_schema, extend_schema_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from authenticacion.api.usecases.auth import GoogleLoginUseCase

@extend_schema_view(
    post=extend_schema(
        tags=["Autenticación"],
        description="Inicia la sesión para el usuario con su cuenta de google.",
    )
)
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = 'http://localhost:3000'  # Adjust this to your frontend URL
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        # Validate token presence
        if 'id_token' in request.data:
            request.data['access_token'] = request.data['id_token']
        elif 'access_token' not in request.data:
            return Response(
                {"error": "No se proporcionó token válido"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Initialize serializer
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)
        
        # Execute use case
        use_case = GoogleLoginUseCase()
        return use_case.execute(
            self.serializer.validated_data['user'],
            self.serializer
        )