from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.socialaccount.models import SocialAccount
from django.core.exceptions import ObjectDoesNotExist
from authenticacion.core.services.stripe.stripe_service import StripeService

User = get_user_model()

class GoogleLoginUseCase:
    """Use case for handling Google login logic."""
    
    def execute(self, social_login, serializer):
        try:
            return self._process_login(social_login)
        except ObjectDoesNotExist:
            return Response(
                {"error": "User not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def _process_login(self, social_login):
        # Get social account and verify email
        social_account = SocialAccount.objects.get(
            user=social_login, 
            provider='google'
        )
        
        if not self._verify_email(social_account):
            return Response(
                {"error": "El email no está verificado"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Update user information
        user = self._update_user_info(social_login, social_account)
        
        # Generate tokens and return response
        return self._generate_response(user)

    def _verify_email(self, social_account):
        extra_data = social_account.extra_data
        return (
            extra_data.get('email_verified', False) or 
            extra_data.get('verified_email', False)
        )

    def _update_user_info(self, social_login, social_account):
        user = User.objects.get(email=social_login.email)
        extra_data = social_account.extra_data
        
        # Update user fields
        user.first_name = extra_data.get('given_name', '')
        user.last_name = extra_data.get('family_name', '')

        # Handle email verification and Stripe customer creation
        if not user.verify_email and self._verify_email(social_account):
            user.is_active = True
            user.verify_email = True
            
            try:
                # Create Stripe customer using the service
                stripe_customer = StripeService.create_customer(user)
                user.customer_id = stripe_customer.id
            except Exception as e:
                raise Exception(f"Error creating Stripe customer: {str(e)}")

        user.save()
        return user

    def _generate_response(self, user):
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        response_data = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'groups': list(user.groups.values_list('name', flat=True)),
                'customer_id': user.customer_id,
                'verify_email': user.verify_email,
                'phone': user.phone
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)