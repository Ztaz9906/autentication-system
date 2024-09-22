from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProvinciaViewSet

router = DefaultRouter()
router.register(r'provincias', ProvinciaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
