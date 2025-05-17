# accounts/signals.py
from django.conf import settings
from django.core.mail import send_mail
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    When a token is created, send an email to the user
    with a link to our Vue reset page.
    """
    # build reset link to your frontend
    reset_url = f"{settings.FRONTEND_URL}/reset-password/{reset_password_token.id}/{reset_password_token.key}"
    
    # simple plain-text email
    message = (
        f"Hi {reset_password_token.user.username},\n\n"
        f"Use the link below to reset your password:\n\n"
        f"{reset_url}\n\n"
        "If you didn’t request this, just ignore this email."
    )
    
    send_mail(
        subject="［YourApp］重設密碼",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[reset_password_token.user.email],
        fail_silently=False,
    )
