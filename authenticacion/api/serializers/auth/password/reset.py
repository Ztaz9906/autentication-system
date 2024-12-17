
from dj_rest_auth.serializers import PasswordResetSerializer
from django.conf import settings
from .reset_form import CustomPasswordResetForm


class CustomPasswordResetSerializer(PasswordResetSerializer):
    password_reset_form_class = CustomPasswordResetForm

    def get_email_options(self):
        context = {
            'frontend_url': settings.SITE_URL,
            'site_name': 'El Chuletazo',
        }
        
        return {
            'subject_template_name': 'account/email/password_reset_key_subject.txt',
            'email_template_name': 'account/email/password_reset_key_message.html',
            'html_email_template_name': 'account/email/password_reset_key_message.html',
            'extra_email_context': context
        }
    