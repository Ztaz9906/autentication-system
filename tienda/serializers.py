from rest_framework import serializers
from authenticacion.serializers import SerializadorUsuarioLectura
from .models import Producto, Precio, Pedido, DetallePedido


class PrecioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Precio
        fields = ['id', 'stripe_price_id', 'unit_amount', 'currency', 'active', 'metadata']


class ProductoSerializer(serializers.ModelSerializer):
    default_price = PrecioSerializer(read_only=True)

    class Meta:
        model = Producto
        fields = ['id', 'stripe_product_id', 'name', 'description', 'active', 'metadata', 'default_price', 'image']


class ProductoDetailSerializer(serializers.ModelSerializer):
    precios = PrecioSerializer(many=True, read_only=True)
    default_price = PrecioSerializer(read_only=True)

    class Meta:
        model = Producto
        fields = ['id', 'stripe_product_id', 'name', 'description', 'active', 'metadata', 'default_price', 'precios', 'image']


class DetallePedidoSerializer(serializers.ModelSerializer):
    precio = PrecioSerializer(read_only=True)
    producto = serializers.SerializerMethodField()

    class Meta:
        model = DetallePedido
        fields = ['id', 'precio', 'cantidad', 'producto']

    def get_producto(self, obj):
        return ProductoSerializer(obj.precio.producto).data


class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ['id', 'usuario', 'total', 'direccion_envio', 'estado', 'stripe_payment_intent_id', 'created_at',
                  'updated_at']


class PedidoDetailSerializer(serializers.ModelSerializer):
    usuario = SerializadorUsuarioLectura(read_only=True)
    detalles = DetallePedidoSerializer(source='detallepedido_set', many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = ['id', 'usuario', 'detalles', 'total', 'direccion_envio', 'estado', 'stripe_payment_intent_id',
                  'created_at', 'updated_at']