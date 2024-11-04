
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from .users import Usuario
from ..utils.constants import TOKEN_EXPIRY_HOURS,TOKEN_LENGTH

class ActivationToken(models.Model):
    """Representa un token de activación para un usuario."""
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='activation_tokens')
    token = models.CharField(max_length=TOKEN_LENGTH, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=TOKEN_EXPIRY_HOURS)  # El token expira en 24 horas
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