from django.contrib.auth import models as auth
from django.db import models
from django.contrib.auth.models import Group as OriginalGroup
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta


class Group(OriginalGroup):
    """Representa un grupo."""
    class Meta:
        proxy = True
        verbose_name = _("Grupo")
        verbose_name_plural = _("Grupos")


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


class ActivationToken(models.Model):
    """Representa un token de activación para un usuario."""
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='activation_tokens')
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)  # El token expira en 24 horas
        super().save(*args, **kwargs)

    @property
    def is_valid(self):
        return timezone.now() <= self.expires_at

    @classmethod
    def delete_expired(cls):
        cls.objects.filter(expires_at__lt=timezone.now()).delete()

    @classmethod
    def clean_expired_tokens(cls):
        deleted_count, _ = cls.objects.filter(expires_at__lt=timezone.now()).delete()
        return deleted_count

    class Meta:
        verbose_name = _("Token de Activación")
        verbose_name_plural = _("Tokens de Activación")