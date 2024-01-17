"""
Módulo necesario para definir la aplicación de documentos (docs)
"""
from django.apps import AppConfig


# noinspection PyMissingOrEmptyDocstring
class DocumentacionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "documentacion"  # INFO: Darse cuenta como se usa el nombre de la aplicación
