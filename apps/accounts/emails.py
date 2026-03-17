from django.core.mail import send_mail
from django.conf import settings

def send_verification_email(user):
    verification_link = f"http://localhost:8000/api/accounts/verify/{user.verification_token}/"
    send_mail(
        subject='Verify your email',
        message=f'Click this link to verify: {verification_link}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
    )
def send_password_reset_email(user):
    reset_link = f"http://localhost:8000/api/accounts/reset-password/{user.password_reset_token}/"
    send_mail(
        subject='Reset your password',
        message=f'Click this link to reset your password: {reset_link}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
    )