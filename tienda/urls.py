from rest_framework import routers
from django.urls import include, path
from .views import PedidoViewSet, ProductoViewSet, StripeWebhookView

# Creamos el router
router = routers.SimpleRouter()
router.register("pedidos", PedidoViewSet)
router.register("productos", ProductoViewSet)


# Definimos las URLs
urlpatterns = [
    path("", include(router.urls)),
    path('webhook/stripe/', StripeWebhookView.as_view(), name='stripe-webhook'),
]
