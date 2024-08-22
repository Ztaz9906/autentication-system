
from django.db import models
from authenticacion.models import Usuario
# Create your models here.


class UnidadMedida(models.Model):
    name = models.CharField(max_length=10, unique=True)
    description = models.TextField(max_length=100)

    def __str__(self):
        return self.name


class Producto(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    stock = models.IntegerField()
    description = models.TextField(max_length=255)
    um = models.ManyToManyField(UnidadMedida)

    def __str__(self):
        return self.name


class Pedido(models.Model):
    productos = models.ManyToManyField(Producto, related_name='pedidos')
    user = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
