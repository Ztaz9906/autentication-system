"""
URLS asociadas a la documentación
"""

# Importamos 'path' para definir nuestras urls
from django.urls import path
from .custom_swagger import CustomSwaggerView


# Definimos las urls
urlpatterns = [
    path(
        "",
        CustomSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
