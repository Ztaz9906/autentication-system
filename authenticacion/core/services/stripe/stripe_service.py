import stripe
from ....utils.exceptions import StripeError

class StripeService:
    @staticmethod
    def create_customer(user):
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=f"{user.first_name} {user.last_name}",
                phone=user.phone
            )
            
            return customer.id
        except stripe.error.StripeError as e:
            raise StripeError(str(e))
        
    @staticmethod
    def delete_customer(customer_id):
        try:
            stripe.Customer.delete(customer_id)
        except stripe.error.StripeError as e:
            raise StripeError(str(e))