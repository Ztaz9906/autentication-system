from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    post=extend_schema(
        tags=["Autenticación"],
        description="Intenta refrescar un token de autenticación.",
    ),
)
class CustomTokenRefreshView(TokenRefreshView):
 ...