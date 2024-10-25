import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .models import Pedido, Producto, Precio, Destinatarios
from .serializers import (
    PedidoSerializer,
    PedidoDetailSerializer,
    ProductoSerializer,
    ProductoDetailSerializer, CreatePedidoSerializer, UpdatePedidoSerializer, DestinatarioSerializer,
    DestinatarioSerializerLectura,
)
import logging
from datetime import datetime, timedelta
from rest_framework.decorators import action
from django.db import transaction
from drf_spectacular.utils import extend_schema, extend_schema_view
from django_filters.rest_framework import DjangoFilterBackend
from authenticacion.models import Usuario
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)

@extend_schema_view(
    list=extend_schema(
        tags=["Pedidos"],
        description="Lista todos los pedidos del usuario o todos los pedidos si es admin"
    ),
    create=extend_schema(
        tags=["Pedidos"],
        description="Crea un nuevo pedido"
    ),
    retrieve=extend_schema(
        tags=["Pedidos"],
        description="Obtiene los detalles de un pedido específico"
    ),
    update=extend_schema(exclude=True),
    partial_update=extend_schema(
        tags=["Pedidos"],
        description="Actualiza parcialmente un pedido"
    ),
    destroy=extend_schema(
        tags=["Pedidos"],
        description="Elimina un pedido"
    ),
)
class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'create':
            return CreatePedidoSerializer
        elif self.action == 'retrieve' or self.action == 'list':
            return PedidoDetailSerializer
        elif self.action == 'partial_update':
            return UpdatePedidoSerializer
        elif self.action == 'cancelar':
            return 
        return PedidoSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Pedido.objects.all()
        return Pedido.objects.filter(usuario=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            pedido = serializer.save()

            line_items = []
            for producto in serializer.validated_data['productos']:
                line_items.append({
                    'price': producto['price'],
                    'quantity': producto['quantity']
                })

            try:
                checkout_session = stripe.checkout.Session.create(
                    customer=serializer.validated_data['customer_id'],
                    payment_method_types=['card'],
                    line_items=line_items,
                    mode='payment',
                    success_url=serializer.validated_data['success_url'],
                    cancel_url=serializer.validated_data['cancel_url'],
                    metadata={'pedido_id': pedido.id},
                    expires_at=int((datetime.now() + timedelta(minutes=60)).timestamp())
                )
                pedido.checkout_session_url = checkout_session.url
                pedido.checkout_session_success_url = checkout_session.success_url
                pedido.checkout_session_cancel_url = checkout_session.cancel_url
                pedido.stripe_checkout_session_id = checkout_session.id
                pedido.save()

                return Response({
                    'checkout_url': checkout_session.url,
                    'pedido_id': pedido.id
                }, status=status.HTTP_201_CREATED)

            except stripe.error.StripeError as e:
                pedido.delete()  # Eliminar el pedido si hay un error con Stripe
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        pedido = self.get_object()
        serializer = self.get_serializer(pedido, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(PedidoDetailSerializer(pedido).data)

    def perform_update(self, serializer):
        serializer.save()

    @extend_schema(
        tags=["Pedidos"],
        description="Retoma el proceso de checkout para un pedido pendiente"
    )
    @action(detail=True, methods=['get'])
    def retomar_checkout(self, request, pk=None):
        pedido = self.get_object()

        if pedido.estado != 'pendiente':
            return Response({'error': 'Este pedido no está pendiente de pago'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            checkout_session = stripe.checkout.Session.retrieve(pedido.stripe_checkout_session_id)

            if checkout_session.status == 'open':
                return Response({'checkout_url': pedido.checkout_session_url})
            elif checkout_session.status == 'expired':
                # Crear una nueva sesión
                new_checkout_session = stripe.checkout.Session.create(
                    customer=pedido.usuario.customer_id,
                    payment_method_types=['card'],
                    line_items=[{
                        'price': detalle.precio.stripe_price_id,
                        'quantity': detalle.cantidad
                    } for detalle in pedido.detallepedido_set.all()],
                    mode='payment',
                    success_url=checkout_session.success_url,
                    cancel_url=checkout_session.cancel_url,
                    metadata={'pedido_id': pedido.id},
                    expires_at=int((datetime.now() + timedelta(minutes=30)).timestamp())
                )
                pedido.checkout_session_url = new_checkout_session.url
                pedido.stripe_checkout_session_id = new_checkout_session.id
                pedido.save()
                return Response({'checkout_url': new_checkout_session.url})
            else:
                return Response({'error': 'La sesión de pago no está disponible'}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=["Pedidos"],
        description="Cancela un pedido pendiente"
    )
    @action(detail=True, methods=['patch'])
    def cancelar(self, request, pk=None):
        pedido = self.get_object()

        if pedido.estado == 'pendiente':
            pedido.estado = 'cancelado'
            pedido.save(update_fields=['estado'])
            return Response({'message': 'Pedido cancelado'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No se puede cancelar un pedido que no está pendiente'}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema_view(
    list=extend_schema(
        tags=["Productos"],
        description="Lista todos los productos"
    ),
    retrieve=extend_schema(
        tags=["Productos"],
        description="Obtiene los detalles de un producto específico"
    ),
    destroy=extend_schema(
        tags=["Productos"],
        description="Elimina un producto"
    ),
    create=extend_schema(exclude=True),
    update=extend_schema(exclude=True),
    partial_update=extend_schema(exclude=True),
)
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'delete', 'head', 'options']
    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return ProductoDetailSerializer
        return ProductoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ['retrieve', 'list']:
            return queryset.prefetch_related('precios').select_related('default_price')
        return queryset


class StripeWebhookView(GenericAPIView):
    @extend_schema(
        tags=["Stripe Webhook"],
        description="Procesa los eventos de webhook de Stripe"
    )
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            logger.error(f"Invalid payload: {str(e)}")
            return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {str(e)}")
            return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if event.type == 'product.created':
                self.handle_product_created(event.data.object)
            elif event.type == 'product.updated':
                self.handle_product_updated(event.data.object)
            elif event.type == 'price.created':
                self.handle_price_created(event.data.object)
            elif event.type == 'price.updated':
                self.handle_price_updated(event.data.object)
            elif event.type == 'product.deleted':
                self.handle_product_deleted(event.data.object)
            elif event.type == 'price.deleted':
                self.handle_price_deleted(event.data.object)
            elif event.type == 'checkout.session.completed':
                self.handle_checkout_session_completed(event.data.object)
            else:
                logger.info(f"Unhandled event type: {event.type}")
                return Response({"message": "Unhandled event type"}, status=status.HTTP_200_OK)

            return Response({"message": "Event processed successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error processing event: {str(e)}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def handle_product_created(self, stripe_product):
        try:
            producto = Producto.objects.create(
                stripe_product_id=stripe_product['id'],
                name=stripe_product['name'],
                description=stripe_product.get('description', ''),
                active=stripe_product['active'],
                metadata=stripe_product.get('metadata', {}),
                image=stripe_product.get('images', [None])[0] if stripe_product.get('images') else None
            )
            logger.info(f"Created new product: {producto.name}")
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            raise

    def handle_product_updated(self, stripe_product):
        try:
            producto = Producto.objects.get(stripe_product_id=stripe_product['id'])
            updated_fields = []

            if producto.name != stripe_product['name']:
                producto.name = stripe_product['name']
                updated_fields.append('name')

            if producto.description != stripe_product.get('description', ''):
                producto.description = stripe_product.get('description', '')
                updated_fields.append('description')

            if producto.active != stripe_product['active']:
                producto.active = stripe_product['active']
                updated_fields.append('active')

            if producto.metadata != stripe_product.get('metadata', {}):
                producto.metadata = stripe_product.get('metadata', {})
                updated_fields.append('metadata')

            image = stripe_product.get('images', [None])[0] if stripe_product.get('images') else None
            if producto.image != image:
                producto.image = image
                updated_fields.append('image')

            if updated_fields:
                producto.save(update_fields=updated_fields)
                logger.info(f"Updated product {producto.name}. Fields updated: {', '.join(updated_fields)}")
            else:
                logger.info(f"No changes detected for product: {producto.name}")

        except Producto.DoesNotExist:
            logger.error(f"Product not found: {stripe_product['id']}")
            raise
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            raise

    def handle_price_created(self, stripe_price):
        try:
            producto, created = Producto.objects.get_or_create(
                stripe_product_id=stripe_price['product'],
                defaults={
                    'name': 'Producto pendiente de actualización',
                    'active': True
                }
            )

            precio = Precio.objects.create(
                stripe_price_id=stripe_price['id'],
                producto=producto,
                unit_amount=stripe_price['unit_amount'],
                currency=stripe_price['currency'],
                active=stripe_price['active'],
                metadata=stripe_price.get('metadata', {})
            )
            logger.info(f"Created new price: {precio.stripe_price_id} for product: {producto.name}")

            if created:
                logger.warning(f"Created placeholder product for price: {stripe_price['id']}")

            # Actualizar el precio por defecto si es necesario
            if not producto.default_price or stripe_price.get('metadata', {}).get('default_price',
                                                                                  'false').lower() == 'true':
                producto.default_price = precio
                producto.save(update_fields=['default_price'])
                logger.info(f"Set new default price for product: {producto.name}")

        except Exception as e:
            logger.error(f"Error creating price: {str(e)}")
            raise


    def handle_price_updated(self, stripe_price):
        try:
            precio = Precio.objects.get(stripe_price_id=stripe_price['id'])
            updated_fields = []

            if precio.unit_amount != stripe_price['unit_amount']:
                precio.unit_amount = stripe_price['unit_amount']
                updated_fields.append('unit_amount')

            if precio.currency != stripe_price['currency']:
                precio.currency = stripe_price['currency']
                updated_fields.append('currency')

            if precio.active != stripe_price['active']:
                precio.active = stripe_price['active']
                updated_fields.append('active')

            if precio.metadata != stripe_price.get('metadata', {}):
                precio.metadata = stripe_price.get('metadata', {})
                updated_fields.append('metadata')

            if updated_fields:
                precio.save(update_fields=updated_fields)
                logger.info(f"Updated price {precio.stripe_price_id}. Fields updated: {', '.join(updated_fields)}")
            else:
                logger.info(f"No changes detected for price: {precio.stripe_price_id}")

            # Check if this price should be the new default
            if stripe_price.get('metadata', {}).get('default_price', 'false').lower() == 'true':
                producto = precio.producto
                if producto.default_price != precio:
                    producto.default_price = precio
                    producto.save(update_fields=['default_price'])
                    logger.info(f"Updated default price for product: {producto.name}")

        except Precio.DoesNotExist:
            logger.error(f"Price not found: {stripe_price['id']}")
            raise
        except Exception as e:
            logger.error(f"Error updating price: {str(e)}")
            raise

    def handle_product_deleted(self, stripe_product):
        try:
            producto = Producto.objects.get(stripe_product_id=stripe_product['id'])
            producto.delete()
            logger.info(f"Deleted product : {producto.name}")
        except Producto.DoesNotExist:
            logger.warning(f"Product not found for deletion: {stripe_product['id']}")
        except Exception as e:
            logger.error(f"Error handling product deletion: {str(e)}")
            raise

    def handle_price_deleted(self, stripe_price):
        try:
            precio = Precio.objects.get(stripe_price_id=stripe_price['id'])
            precio.active = False
            precio.save(update_fields=['active'])
            logger.info(f"Marked price as inactive: {precio.stripe_price_id}")

            # If this was the default price, unset it
            producto = precio.producto
            if producto.default_price == precio:
                producto.default_price = None
                producto.save(update_fields=['default_price'])
                logger.info(f"Unset default price for product: {producto.name}")

        except Precio.DoesNotExist:
            logger.warning(f"Price not found for deletion: {stripe_price['id']}")
        except Exception as e:
            logger.error(f"Error handling price deletion: {str(e)}")
            raise

    def handle_checkout_session_completed(self, stripe_checkout_session):
        try:
            pedido = Pedido.objects.get(stripe_checkout_session_id=stripe_checkout_session['id'])
            pedido.estado = 'pagado'
            pedido.save(update_fields=['estado'])
            logger.info(f"Marked pedido as completed: {pedido.estado}")

        except Pedido.DoesNotExist:
            logger.warning(f"Checkout session not found: {stripe_checkout_session['id']}")

        except Exception as e:
            logger.error(f"Error handling checkout session completion: {str(e)}")
            raise


@extend_schema_view(
    list=extend_schema(
        tags=["Destinatarios"],
        description="Lista todos Destinatarios",
    ),
    retrieve=extend_schema(
        tags=["Destinatarios"],
        description="Obtiene los detalles de un Destinatario"
    ),
    destroy=extend_schema(
        tags=["Destinatarios"],
        description="Elimina un Destinatario"),
    create=extend_schema(
        tags=["Destinatarios"],
        description="Crea  un Destinatario"),
    update=extend_schema(
        tags=["Destinatarios"],
        description="Edita los detalles de un Destinatario"),

    partial_update=extend_schema(
        tags=["Destinatarios"],
        description="Edita los detalles de un Destinatario"),
)
class DestinatarioViewSet(viewsets.ModelViewSet):
    queryset = Destinatarios.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["ci", 'usuario__id', 'nombre', 'apellidos']
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            return DestinatarioSerializerLectura
        return DestinatarioSerializer

    # Sobrescribimos el queryset para filtrar por usuario actual si no es superuser
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Destinatarios.objects.all()
        else:
            return Destinatarios.objects.filter(usuario=self.request.user)


    # Modificar el create para manejar tanto la creación como la actualización basada en CI
    def create(self, request, *args, **kwargs):
        ci = request.data.get('ci')
        usuario_id = request.user.id
        usuario = get_object_or_404(Usuario, id=usuario_id)

        try:
            # Intentar obtener el destinatario por su CI
            destinatario = Destinatarios.objects.get(ci=ci)

            # El destinatario ya existe, actualizamos sus datos
            serializer = self.get_serializer(destinatario, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            # Añadimos el usuario al destinatario si no está ya

            destinatario.usuario.add(usuario)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Destinatarios.DoesNotExist:
            # El destinatario no existe, lo creamos
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            destinatario = serializer.save()
            destinatario.usuario.add(usuario)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # Modificar destroy para eliminar solo el usuario o el destinatario completo
    def destroy(self, request, *args, **kwargs):
        destinatario = self.get_object()
        usuario_id = request.user.id
        
        if not usuario_id:
            return Response(
                {"error": "Se requiere el ID del usuario"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if destinatario.usuario.count() > 1:
            usuario = get_object_or_404(Usuario, id=usuario_id)
            destinatario.usuario.remove(usuario)
            
            return Response(
                {"message": f"El usuario con ID {usuario_id} fue eliminado del destinatario."},
                status=status.HTTP_200_OK  # Cambiado de 204 a 200
            )
        else:
            if Pedido.objects.filter(destinatario=destinatario).exists():
                return Response(
                    {"message": "No se puede eliminar el destinatario porque está asociado a uno o más pedidos."},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            self.perform_destroy(destinatario)
            return Response(
                {"message": "El destinatario fue eliminado completamente."},
                status=status.HTTP_200_OK
            )
