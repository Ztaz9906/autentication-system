from rest_framework import routers
from django.urls import include, path
from .views import PedidoViewSet, ProductoViewSet, UnidadMedidaViewSet

# Creamos el router
router = routers.SimpleRouter()
router.register("pedidos", PedidoViewSet)
router.register("productos", ProductoViewSet)
router.register("unidades-de-medida", UnidadMedidaViewSet)

# Definimos las URLs
urlpatterns = [
    path("", include(router.urls)),
]
