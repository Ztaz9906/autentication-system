from rest_framework import serializers
from authenticacion.models import Usuario, Group
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from django.contrib.auth.models import Permission
from dj_rest_auth.serializers import PasswordResetSerializer
from django.contrib.auth import get_user_model
import string
import random


class CustomLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')

        if not (username or email):
            msg = 'Debe proporcionar "username" o "email".'
            raise serializers.ValidationError(msg, code='authorization')

        if not password:
            msg = 'Debe proporcionar "password".'
            raise serializers.ValidationError(msg, code='authorization')

        user = None
        user_model = get_user_model()

        if username:
            try:
                user = user_model.objects.get(username=username)
            except user_model.DoesNotExist:
                pass

        if not user and email:
            try:
                user = user_model.objects.get(email=email)
            except user_model.DoesNotExist:
                pass

        if user and user.check_password(password):
            attrs['user'] = user
            return attrs

        msg = 'No se puede iniciar sesión con las credenciales proporcionadas.'
        raise serializers.ValidationError(msg, code='authorization')


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(help_text="El token de actualización que debe deshabilitarse")

    class Meta:
        fields = ['refresh_token']

@extend_schema_serializer(component_name="SerializadorDePermisos")
class SerializadorDePermisos(serializers.ModelSerializer):
    """Clase encargada de serializar y deserializar los permisos."""

    class Meta:
        model = Permission
        fields = ("id", "name", "codename")


@extend_schema_serializer(component_name="SerializadorDeGruposLectura")
class SerializadorDeGruposLectura(serializers.ModelSerializer):
    """Clase encargada de serializar y deserializar los grupos."""

    permissions = SerializadorDePermisos(many=True)

    class Meta:
        model = Group
        fields = ["id", "name", "permissions"]


@extend_schema_serializer(component_name="SerializadorDeGrupos")
class SerializadorDeGrupos(serializers.ModelSerializer):
    """Clase encargada de serializar y deserializar los grupos."""
    class Meta:
        model = Group
        fields = ["id", "name", "permissions"]


class SerializadorUsuarioLectura(serializers.ModelSerializer):
    """Clase base utilizada en la serialización/deserialización de los usuarios."""
    groups = SerializadorDeGruposLectura(many=True)
    user_permissions = SerializadorDePermisos(many=True)

    class Meta:
        model = Usuario
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "groups",
            "user_permissions",
            'customer_id'
        ]


class SerializadorDeUsuarioEscritura(serializers.ModelSerializer):
    """Clase encargada de serializar y deserializar los usuarios."""

    password = serializers.CharField(write_only=True)

    def generate_unique_username(self):
        """Genera un nombre de usuario aleatorio y único."""
        while True:
            # Generar un nombre de usuario aleatorio con letras y números
            username = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

            # Comprobar si ya existe un usuario con este nombre
            if not Usuario.objects.filter(username=username).exists():
                return username

    def create(self, validated_data):
        # Generar un nombre de usuario único
        validated_data['username'] = self.generate_unique_username()

        # Crear el usuario
        user = super().create(validated_data)
        user.set_password(validated_data['password'])  # Guardar la contraseña
        user.save()
        return user

    class Meta:
        model = Usuario
        fields = [
            "email",
            'password',
            "first_name",
            "last_name",
            'phone',
            "groups",
            "user_permissions",
        ]

class SerializadorDeGrupoAuth(serializers.ModelSerializer):
    """Clase encargada de serializar y deserializar los grupos."""
    class Meta:
        model = Group
        fields = ["name"]


class SerializadorUsuarioAuth(serializers.ModelSerializer):
    """Clase base utilizada en la serialización/deserialización de los usuarios autenticados."""
    groups = SerializadorDeGrupoAuth(many=True)

    class Meta:
        model = Usuario
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "groups",
            'customer_id',
            'phone'
        ]


@extend_schema_serializer(
    component_name="ReseteoDePassword",
    examples=[
        OpenApiExample(
            name="Reset comenzado",
            value={
                "detail": "string",
            },
            response_only=True,
        )
    ],
)
class CustomPasswordResetSerializer(PasswordResetSerializer):

    url = serializers.URLField()

    def get_email_options(self):
        return super().get_email_options() | {
            "subject_template_name": "email/subject.txt",
            "email_template_name": "email/empty_body.html",
            "use_https": True,
            "extra_email_context": {
                "url": self.data["url"],
                "site_name": "LocalHost",
            },
        }
