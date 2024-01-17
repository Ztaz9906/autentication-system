"""
URLS asociadas a la documentación
"""

# Importamos 'path' para definir nuestras urls
from django.urls import path

from .custom_spectacular import CustomSpectacularApiView

# Definimos las urls
urlpatterns = [
    path("schema/", CustomSpectacularApiView.as_view(), name="schema"),
]
