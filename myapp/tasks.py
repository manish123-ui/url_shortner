
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_otp_email(name, email, otp):
    subject = "Verify your Shortiurl Account"
    message = f"Hello {name},\n\nYour OTP is {otp}. It is valid for 5 minutes.\n\nThanks,\nShortiurl Team"
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)
    return f"OTP email sent to {email}"
