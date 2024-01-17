from rest_framework import serializers
from authenticacion.models import Usuario, Group
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from django.contrib.auth.models import Permission
from dj_rest_auth.serializers import PasswordResetSerializer


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
        ]


class SerializadorDeUsuarioEscritura(serializers.ModelSerializer):
    """Clase encargada de serializar y deserializar los usuarios."""

    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = Usuario
        fields = [
            "username",
            "email",
            'password',
            "first_name",
            "last_name",
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
