from django.core.mail import send_mail
from django.conf import settings


def send_verification_email(user):
    verification_link = f"http://localhost:8000/api/accounts/verify-email/{user.verification_token}/"
    send_mail(
        subject='Verify your email',
        message=f'Welcome! Please click this link to verify your email address:\n\n{verification_link}\n\nThis link expires in 24 hours.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False,
    )

def send_password_reset_email(user):
    reset_link = f"http://localhost:3000/forgot-password?token={user.password_reset_token}"
    send_mail(
        subject='Reset your password',
        message=f'You requested a password reset. Click this link to reset your password:\n\n{reset_link}\n\nThis link expires in 1 hour.\n\nIf you didn\'t request this, please ignore this email.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False,
    )

def send_otp_email(user, otp):
    send_mail(
        subject='Your Login OTP',
        message=f'Your login OTP code is: {otp}\n\nThis code expires in 5 minutes.\n\nIf you didn\'t try to login, please ignore this email.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False,
    )