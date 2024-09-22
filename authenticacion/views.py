from authenticacion.models import Usuario, Group
from authenticacion.serializers import SerializadorUsuarioLectura, SerializadorDeUsuarioEscritura, SerializadorDeGrupos, SerializadorDeGruposLectura, CustomPasswordResetSerializer, LogoutSerializer, CustomLoginSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import permissions, viewsets, status
from django_filters import rest_framework as filters
from dj_rest_auth.views import LoginView, LogoutView, PasswordResetView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.response import Response
import stripe
from allauth.socialaccount.models import SocialAccount
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


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

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SerializadorUsuarioLectura
        return SerializadorDeUsuarioEscritura

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Crear el usuario en Django
        user = serializer.save()

        try:
            # Crear el cliente en Stripe
            print("Intentando crear cliente en Stripe...")
            stripe_customer = stripe.Customer.create(
                email=user.email,
                name=f"{user.first_name} {user.last_name}"
            )

            # Guardar el ID del cliente de Stripe en el modelo de usuario
            user.customer_id = stripe_customer.id
            user.save()

        except stripe.error.StripeError as e:
            # Si hay un error al crear el cliente en Stripe, eliminar el usuario de Django
            user.delete()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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
    serializer_class = CustomLoginSerializer


@extend_schema_view(
    post=extend_schema(
        tags=["Autenticación"],
        request=LogoutSerializer,
        description="Confirma el borrado de la sesión del usuario actual",
    ),
    get=extend_schema(exclude=True),
)
class CustomLogoutView(LogoutView):
    """Borra el token y la sesión asignada al usuario actual."""

    serializer_class = LogoutSerializer


@extend_schema_view(
    post=extend_schema(
        tags=["Autenticación"],
        description="Inicia el proceso de recuperación de contraseña.",
    )
)
class CustomPasswordResetView(PasswordResetView):
    """Comienza el flujo de reseteo de passwords."""

    serializer_class = CustomPasswordResetSerializer


User = get_user_model()

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

        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        if 'id_token' in self.request.data:
            self.request.data['access_token'] = self.request.data['id_token']

        self.serializer.is_valid(raise_exception=True)
        social_login = self.serializer.validated_data['user']
        email = social_login.email

        try:
            social_account = SocialAccount.objects.get(user=social_login, provider='google')
            extra_data = social_account.extra_data
            email_verified = extra_data.get('email_verified', False)
            if not email_verified:
                print(f'Error: El email {email} no está verificado por Google')
                return Response({"error": "El email no está verificado"}, status=status.HTTP_403_FORBIDDEN)

            user = User.objects.get(email=email)
            user.first_name = extra_data.get('given_name', '')
            user.last_name = extra_data.get('family_name', '')

            if not user.verify_email and email_verified:
                user.verify_email = True
                user.save()
                print('Email verified')

                try:
                    print('Creating Stripe customer')
                    stripe_customer = stripe.Customer.create(
                        email=user.email,
                        name=f"{user.first_name} {user.last_name}"
                    )
                    user.customer_id = stripe_customer.id
                    user.save()
                    print(f'Stripe customer created and ID saved: {stripe_customer.id}')
                except stripe.error.StripeError as e:
                    print(f'Error creating Stripe customer: {str(e)}')
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                user.save()

        except ObjectDoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        print('Login successful')
        return self.get_response(user, access_token, refresh_token)

    def get_response(self, user, access_token, refresh_token):
        data = {
            'access': access_token,
            'refresh': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'groups': list(user.groups.values_list('name', flat=True)),
                'customer_id': user.customer_id,
                'verify_email': user.verify_email
            }
        }
        return Response(data, status=status.HTTP_200_OK)
