from rest_framework import routers
from authenticacion.views import (VistasDeUsuarios, CustomLoginView, VistasDeGrupos, CustomLogoutView,CustomPasswordResetView,GoogleLogin)
from rest_framework_simplejwt.views import (TokenRefreshView, TokenVerifyView)
from django.urls import include, path
from dj_rest_auth.views import (PasswordChangeView, PasswordResetView,PasswordResetConfirmView)
router = routers.SimpleRouter()
router.register("usuarios", VistasDeUsuarios)
router.register("grupos", VistasDeGrupos)

# Definimos las urls
urlpatterns = [
    path('google-login/', GoogleLogin.as_view(), name='google_login'),
    path("login/", CustomLoginView.as_view(), name="api-login"),
    path("logout/", CustomLogoutView.as_view(), name="api-logout"),
    path("change_password", PasswordChangeView.as_view()),
    path("reset_password", CustomPasswordResetView.as_view()),
    path("reset_password_confirm", PasswordResetConfirmView.as_view()),
    path("token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("", include(router.urls)),
]


