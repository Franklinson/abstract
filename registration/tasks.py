from celery import shared_task
from django.core.mail import send_mail, mail_admins
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from abstract.models import  EmailLog




@shared_task
def send_email_task(email_type, subject, recipient, template_name, context, is_admin=False):
    """
    Celery task to send emails and log them.
    """
    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)

    if is_admin:
        mail_admins(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            fail_silently=False,
        )
    else:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            html_message=html_message,
            fail_silently=False,
        )

    # Log the email
    EmailLog.objects.create(
        recipient=recipient,
        subject=subject,
        plain_message=plain_message,
        html_message=html_message,
    )