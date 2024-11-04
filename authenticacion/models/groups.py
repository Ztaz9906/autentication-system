from django.contrib.auth.models import Group as OriginalGroup
from django.utils.translation import gettext_lazy as _



class Group(OriginalGroup):
    """Representa un grupo."""
    class Meta:
        proxy = True
        verbose_name = _("Grupo")
        verbose_name_plural = _("Grupos")