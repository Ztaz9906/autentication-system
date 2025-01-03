from django.contrib.auth import models as auth
from django.db import models
from django.utils.translation import gettext_lazy as _


class Usuario(auth.AbstractUser):
    """Representa un usuario."""
    is_active = models.BooleanField(default=False)
    email = models.EmailField(_("email address"), unique=True)
    customer_id = models.CharField(_("customer id"), blank=True, null=True, unique=True)
    verify_email = models.BooleanField(_("verify email"), default=False)
    phone = models.CharField(_("phone number"), blank=True, null=True, unique=True)

    class Meta(auth.AbstractUser.Meta):
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"