"""
URLS asociadas a la documentación
"""

# Importamos 'path' para definir nuestras urls
from django.urls import path, include

# Definimos las urls
urlpatterns = [
    path("", include("documentacion.views.api.urls")),
    path("", include("documentacion.views.web.urls")),
]
