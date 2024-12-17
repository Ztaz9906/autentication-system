
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.contrib.auth.forms import PasswordResetForm

class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                 context, from_email, to_email, html_email_template_name=None):
        """
        Override para asegurar que el contexto extra se pase al template
        """
        context.update(context.get('extra_email_context', {}))
        
        subject = get_template(subject_template_name).render(context)
        subject = ''.join(subject.splitlines())
        
        body = get_template(email_template_name).render(context)
        
        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        
        if html_email_template_name:
            html_email = get_template(html_email_template_name).render(context)
            email_message.attach_alternative(html_email, 'text/html')
        
        email_message.send()
