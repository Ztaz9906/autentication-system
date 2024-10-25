from authenticacion.models import Usuario, Group, ActivationToken
from authenticacion.serializers import SerializadorUsuarioLectura, SerializadorDeUsuarioEscritura, SerializadorDeGrupos, SerializadorDeGruposLectura, CustomPasswordResetSerializer, LogoutSerializer, CustomLoginSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
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
from django.conf import settings
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from rest_framework.decorators import action
from django.template.loader import render_to_string
from django.utils.html import strip_tags


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

        # Crear el usuario en Django (inicialmente inactivo)
        user = serializer.save(is_active=False)

        try:
            # Crear el cliente en Stripe
            print("Intentando crear cliente en Stripe...")
            stripe_customer = stripe.Customer.create(
                email=user.email,
                name=f"{user.first_name} {user.last_name}",
                phone=user.phone
            )

            # Guardar el ID del cliente de Stripe en el modelo de usuario
            user.customer_id = stripe_customer.id
            user.save()

            # Crear token de activación
            token = get_random_string(64)
            ActivationToken.objects.create(user=user, token=token)

            # Enviar correo de activación
            self.send_activation_email(user, token)

        except stripe.error.StripeError as e:
            # Si hay un error al crear el cliente en Stripe, eliminar el usuario de Django
            user.delete()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Si hay un error al enviar el correo, eliminar el usuario de Django y el cliente de Stripe
            stripe.Customer.delete(user.customer_id)
            user.delete()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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
        """Activa un usuario a partir del token de activación."""
        token = request.data.get('token')

        if not token:
            return Response({"error": "Token no proporcionado"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Buscar el token de activación
            activation_token = ActivationToken.objects.get(token=token)

            # Verificar si el token ha expirado
            if not activation_token.is_valid:
                return Response({"error": "El token ha expirado"}, status=status.HTTP_400_BAD_REQUEST)

            user = activation_token.user

            # Activar el usuario
            user.is_active = True
            user.save()

            # Eliminar el token de activación
            activation_token.delete()

            return Response({"message": "Usuario activado correctamente"}, status=status.HTTP_200_OK)

        except ActivationToken.DoesNotExist:
            return Response({"error": "El token es inválido"}, status=status.HTTP_400_BAD_REQUEST)

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
        """Reenvía el correo de activación si el token ha expirado o no ha llegado."""
        email = request.data.get('email')

        if not email:
            return Response({"error": "Email no proporcionado"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Buscar el usuario por su email
            user = Usuario.objects.get(email=email)

            if user.is_active:
                return Response({"error": "Este usuario ya está activado."}, status=status.HTTP_400_BAD_REQUEST)

            # Generar un nuevo token de activación
            token = get_random_string(64)

            # Actualizar o crear el nuevo token de activación
            ActivationToken.objects.update_or_create(user=user, defaults={'token': token})

            # Enviar el nuevo correo de activación
            self.send_activation_email(user, token)

            return Response({"message": "Correo de activación reenviado"}, status=status.HTTP_200_OK)

        except Usuario.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_400_BAD_REQUEST)

    def send_activation_email(self, user, token):

        subject = 'Activa tu cuenta en El Chuletazo'
        activation_link = f"{settings.SITE_URL}/activate/{token}/"
    
        # Contexto para el template
        context = {
            'first_name': user.first_name,
            'activation_link': activation_link
        }
        
        # Renderiza el template HTML
        print('Sending activation email...')
        html_message = render_to_string('emails/account_activation.html', context)
        # Crea una versión texto plano del email
        plain_message = strip_tags(html_message)
        subject = 'Activa tu cuenta'
        activation_link = f"{settings.SITE_URL}/activate/{token}/"
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

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
        elif 'access_token' not in self.request.data:
            return Response({"error": "No se proporcionó token válido"}, status=status.HTTP_400_BAD_REQUEST)

        self.serializer.is_valid(raise_exception=True)
        social_login = self.serializer.validated_data['user']
        email = social_login.email

        try:
            social_account = SocialAccount.objects.get(user=social_login, provider='google')
            extra_data = social_account.extra_data
            print(extra_data)

            email_verified = False
            if 'email_verified' in extra_data:
                email_verified = extra_data.get('email_verified', False)
            elif 'verified_email' in extra_data:
                email_verified = extra_data.get('verified_email', False)
            if not email_verified:
                print(f'Error: El email {email} no está verificado por Google')
                return Response({"error": "El email no está verificado"}, status=status.HTTP_403_FORBIDDEN)

            user = User.objects.get(email=email)
            user.first_name = extra_data.get('given_name', '')
            user.last_name = extra_data.get('family_name', '')

            if not user.verify_email and email_verified:
                user.is_active = True
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
                'verify_email': user.verify_email,
                'phone': user.phone
            }
        }
        return Response(data, status=status.HTTP_200_OK)
