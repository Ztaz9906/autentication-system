from rest_framework import serializers
from .models import Producto, Precio, Pedido, DetallePedido, Destinatarios
from nomencladores.serializers import MunicipioSerializer, ProvinciaDestinatarioSerializer
from django.core.cache import cache
from authenticacion.models.users import Usuario
class DestinatarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destinatarios
        fields = ['id', 'direccion', 'ci', 'provincia',
                  'apellidos', 'municipio', 'nombre',
                  'numero_casa', 'telefono_celular',
                  'telefono_fijo']


class DestinatarioSerializerLectura(serializers.ModelSerializer):
    municipio = MunicipioSerializer(read_only=True)
    provincia = ProvinciaDestinatarioSerializer(read_only=True)
    class Meta:
        model = Destinatarios
        fields = [ 'id','direccion', 'ci', 'provincia',
                  'apellidos', 'municipio', 'nombre',
                  'numero_casa', 'telefono_celular',
                  'telefono_fijo',]
        
class DestinatarioSerializerPedidoLectura(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    provincia = ProvinciaDestinatarioSerializer(read_only=True)
    class Meta:
        model = Destinatarios
        fields = ['nombre_completo','provincia']
    
    def get_nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellidos}"
    
class RemitenteSerializerPedidoLectura(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    class Meta:
        model = Usuario
        fields = ['nombre_completo', 'email']
    def get_email(self, obj):
        return obj.email
    def get_nombre_completo(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class ProductoEnPedidoSerializer(serializers.Serializer):
    stripe_product_id = serializers.CharField()
    price = serializers.CharField()
    quantity = serializers.IntegerField(min_value=1)


class CreatePedidoSerializer(serializers.Serializer):
    destinatario_id = serializers.IntegerField(required=True)
    customer_id = serializers.CharField(required=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    productos = ProductoEnPedidoSerializer(many=True,required=True)
    success_url = serializers.URLField(required=True)
    cancel_url = serializers.URLField(required=True)

    def validate_productos(self, value):
        for producto in value:
            try:
                Producto.objects.get(stripe_product_id=producto['stripe_product_id'])
            except Producto.DoesNotExist:
                raise serializers.ValidationError(f"Producto con ID {producto['stripe_product_id']} no existe")

            try:
                Precio.objects.get(stripe_price_id=producto['price'],
                                   producto__stripe_product_id=producto['stripe_product_id'])
            except Precio.DoesNotExist:
                raise serializers.ValidationError(
                    f"Precio con ID {producto['price']} no existe para el producto {producto['stripe_product_id']}")
        return value

    def create(self, validated_data):
        usuario = self.context['request'].user
        destinatario =  Destinatarios.objects.get(id=validated_data['destinatario_id'])
        pedido = Pedido.objects.create(
            usuario=usuario,
            destinatario=destinatario,
            total=validated_data['total'],
            checkout_session_success_url=validated_data['success_url'],
            checkout_session_cancel_url=validated_data['cancel_url']
        )

        for producto_data in validated_data['productos']:
            precio = Precio.objects.get(stripe_price_id=producto_data['price'])
            DetallePedido.objects.create(
                pedido=pedido,
                precio=precio,
                cantidad=producto_data['quantity']
            )

        return pedido


class PrecioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Precio
        fields = ['id', 'stripe_price_id', 'unit_amount', 'currency', 'active', 'metadata']


class ProductoSerializer(serializers.ModelSerializer):
    default_price = PrecioSerializer(read_only=True)

    class Meta:
        model = Producto
        fields = ['id', 'stripe_product_id', 'name', 'description', 'active', 'metadata', 'default_price', 'image','category']


class ProductoDetailSerializer(serializers.ModelSerializer):
    precios = PrecioSerializer(many=True, read_only=True)
    default_price = PrecioSerializer(read_only=True)

    class Meta:
        model = Producto
        fields = ['id', 'stripe_product_id', 'name', 'description', 'active', 'metadata', 'default_price', 'precios', 'image','category']


class DetallePedidoSerializer(serializers.ModelSerializer):
    producto = serializers.SerializerMethodField()

    class Meta:
        model = DetallePedido
        fields = ['producto', 'cantidad']

    def get_producto(self, obj):
        return ProductoSerializer(obj.precio.producto).data


class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ['id', 'usuario', 'total', 'destinatario', 'estado', 'stripe_checkout_session_id', 'created_at',
                  'updated_at', 'productos', 'checkout_session_url']


class PedidoListSerializer(serializers.ModelSerializer):

    destinatario = DestinatarioSerializerPedidoLectura(read_only=True)

    usuario = RemitenteSerializerPedidoLectura(read_only=True)
    class Meta:
        model = Pedido
        fields = ['id', 'total', 'destinatario', 'estado', 'created_at','usuario']
    
class PedidoRetrieveSerializer(serializers.ModelSerializer):
    productos = DetallePedidoSerializer(source='detallepedido_set', many=True, read_only=True)
    destinatario = DestinatarioSerializerLectura(read_only=True)

    class Meta:
        model = Pedido
        fields = ['productos', 'total', 'destinatario', 'estado',
                  'created_at', 'updated_at']
        
    def to_representation(self, instance):
        # Optimizamos el cacheo por objeto individual
        cache_key = f'pedido_retrieve_{instance.id}'
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return cached_data
            
        representation = super().to_representation(instance)
        cache.set(cache_key, representation, timeout=300)  # 5 minutos
        return representation

class ProductoEnPedidoUpdateSerializer(serializers.Serializer):
    stripe_product_id = serializers.CharField()
    quantity = serializers.IntegerField(min_value=1)


class UpdatePedidoSerializer(serializers.ModelSerializer):
    productos = ProductoEnPedidoUpdateSerializer(many=True, required=False)

    class Meta:
        model = Pedido
        fields = ['estado', 'productos']

    def validate(self, data):
        user = self.context['request'].user
        pedido = self.instance

        if not user.is_superuser and pedido.estado not in ['pendiente', 'pagado']:
            raise serializers.ValidationError("No se puede editar este pedido en su estado actual.")

        if 'estado' in data:
            if not user.is_superuser:
                raise serializers.ValidationError("Solo los administradores pueden cambiar el estado del pedido.")
            if pedido.estado == 'pagado' and data['estado'] not in ['enviado', 'entregado']:
                raise serializers.ValidationError("El estado solo puede cambiarse a 'enviado' o 'entregado'.")
            if pedido.estado == 'enviado' and data['estado'] != 'entregado':
                raise serializers.ValidationError("El estado solo puede cambiarse a 'entregado'.")

        if 'productos' in data and pedido.estado != 'pendiente':
            raise serializers.ValidationError("Solo se pueden modificar productos en pedidos pendientes.")

        return data

    def update(self, instance, validated_data):
        productos_data = validated_data.pop('productos', None)

        # Actualizar campos simples del pedido
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if productos_data:
            self.actualizar_productos(instance, productos_data)

        # Recalcular el total del pedido
        instance.total = self.calcular_total(instance)
        instance.save()
        return instance

    def actualizar_productos(self, pedido, productos_data):
        for producto_data in productos_data:
            stripe_product_id = producto_data['stripe_product_id']
            cantidad = producto_data['quantity']

            try:
                producto = Producto.objects.get(stripe_product_id=stripe_product_id)
                precio = producto.default_price
            except Producto.DoesNotExist:
                raise serializers.ValidationError(f"Producto con ID {stripe_product_id} no existe")

            detalle, created = DetallePedido.objects.update_or_create(
                pedido=pedido,
                precio=precio,
                defaults={'cantidad': cantidad}
            )

    def calcular_total(self, pedido):
        return sum(
            detalle.precio.unit_amount * detalle.cantidad
            for detalle in pedido.detallepedido_set.all()
        ) / 100


class UpdatePedidoEstadoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Pedido
        fields = ['estado']

    def validate(self, data):
        user = self.context['request'].user
        pedido = self.instance
 
        if 'estado' in data:
            if not user.is_superuser:
                raise serializers.ValidationError("Solo los administradores pueden cambiar el estado del pedido.")
            if pedido.estado == 'pagado' and data['estado'] != 'enviado' :
                raise serializers.ValidationError("El estado solo puede cambiarse a 'enviado'.")
            if pedido.estado == 'enviado' and data['estado'] != 'entregado':
                raise serializers.ValidationError("El estado solo puede cambiarse a 'entregado'.")
            if pedido.estado not in ['pagado', 'enviado']:
                raise serializers.ValidationError("El estado solo puede cambiarse si el pedido está en 'pagado' o 'enviado'.")
        return data

    def update(self, instance, validated_data):
   
        # Actualizar campos simples del pedido
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

