from rest_framework import routers
from django.urls import include, path
from authenticacion.api.views import CustomLoginView,CustomLogoutView,CustomPasswordResetView,CustomPasswordChangeView,CustomTokenVerifyView,CustomTokenRefreshView,GoogleLogin,VistasDeUsuarios,VistasDeGrupos,CustomPasswordResetConfirmView




router = routers.SimpleRouter()
router.register("usuarios", VistasDeUsuarios)
router.register("grupos", VistasDeGrupos)

# Definimos las urls
urlpatterns = [
    path('google-login/', GoogleLogin.as_view(), name='google_login'),
    path("login/", CustomLoginView.as_view(), name="api-login"),
    path("logout/", CustomLogoutView.as_view(), name="api-logout"),
    path("change_password", CustomPasswordChangeView.as_view()),
    path("reset_password", CustomPasswordResetView.as_view(),name="password_reset"),
    path("reset_password_confirm/<uidb64>/<token>/", 
         CustomPasswordResetConfirmView.as_view(), 
         name="password_reset_confirm"),
    path("token/verify/", CustomTokenVerifyView.as_view(), name="token-verify"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token-refresh"),
    path("", include(router.urls)),
]


