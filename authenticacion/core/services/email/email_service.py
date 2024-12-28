from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


class EmailService:
    @staticmethod
    def send_activation_email(user, token):
        context = {
            'first_name': user.first_name,
            'activation_link': f"{settings.SITE_URL}/activate/{token}/"
        }
        
        html_message = render_to_string('emails/account_activation.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject='Activa tu cuenta',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
    @staticmethod
    def send_superuser_activation_email(user, token):
        context = {
            'first_name': user.first_name,
            'activation_link': f"{settings.SITE_URL}/activate/{token}/"
        }
        
        html_message = render_to_string('emails/super_user_activation_link.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject='Activa tu cuenta',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['staff@elchuletazo.com'],
            html_message=html_message,
            fail_silently=False,
        )