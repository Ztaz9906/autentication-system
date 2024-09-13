from django.db import models
from authenticacion.models import Usuario

class Producto(models.Model):
    stripe_product_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=255,null=True, blank=True)
    active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    default_price = models.ForeignKey('Precio', on_delete=models.SET_NULL, null=True, related_name='default_for_products')
    image = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name

class Precio(models.Model):
    stripe_price_id = models.CharField(max_length=100, unique=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='precios')
    unit_amount = models.IntegerField()  # en centavos
    currency = models.CharField(max_length=3)
    active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.producto.name} - {self.unit_amount/100} {self.currency}"

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Precio, through='DetallePedido')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    direccion_envio = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    stripe_checkout_session_id = models.CharField(max_length=100, blank=True, null=True)
    checkout_session_url = models.URLField(max_length=500, blank=True, null=True)
    checkout_session_success_url = models.URLField(max_length=500, blank=True, null=True)
    checkout_session_cancel_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido {self.id} - {self.usuario.username}"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    precio = models.ForeignKey(Precio, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.pedido.id} - {self.precio.producto.name} x {self.cantidad}"