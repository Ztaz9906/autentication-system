import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Pedido, Producto, Precio
from .serializers import (
    PedidoSerializer,
    PedidoDetailSerializer,
    ProductoSerializer,
    ProductoDetailSerializer,
)
import logging

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PedidoDetailSerializer
        return PedidoSerializer


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return ProductoDetailSerializer
        return ProductoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ['retrieve', 'list']:
            return queryset.prefetch_related('precios').select_related('default_price')
        return queryset


class StripeWebhookView(APIView):
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