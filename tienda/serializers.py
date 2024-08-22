from rest_framework import serializers

from authenticacion.serializers import SerializadorUsuarioLectura
from .models import UnidadMedida, Producto, Pedido


class UnidadMedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadMedida
        fields = '__all__'


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'


class ProductoSerializerLectura(serializers.ModelSerializer):
    um = UnidadMedidaSerializer(many=True)

    class Meta:
        model = Producto
        fields = '__all__'


class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = '__all__'


class PedidoSerializerLectura(serializers.ModelSerializer):
    productos = ProductoSerializerLectura(many=True)
    user = SerializadorUsuarioLectura()

    class Meta:
        model = Pedido
        fields = '__all__'
