from django.contrib.auth import models as auth
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group as OriginalGroup
from django.utils.translation import gettext_lazy as _


class Group(OriginalGroup):
    """Representa un grupo."""
    class Meta:
        proxy = True
        verbose_name = _("Grupo")
        verbose_name_plural = _("Grupos")


class Usuario(auth.AbstractUser):
    """Representa un usuario."""
    email = models.EmailField(_("email address"), unique=True)

    class Meta(auth.AbstractUser.Meta):
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

