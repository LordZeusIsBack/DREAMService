import secrets
from django.core.cache import caches
from django.core.mail import send_mail
from django.conf import settings

otp_handler_cache = caches['otp_handler_cache']

def generate_otp(length=6): return str(secrets.randbelow(10 * length)).zfill(length)

def send_otp(email):
    otp = generate_otp()
    otp_handler_cache.set(f"otp_{email}", otp, timeout=settings.OTP_TIMEOUT)

    send_mail(
        subject="Your Verification OTP",
        message=f"Your OTP is {otp}. It is valid for 5 minutes.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )

def verify_otp(email, input_otp):
    stored_otp = otp_handler_cache.get(f"otp_{email}")
    if stored_otp and stored_otp == input_otp:
        otp_handler_cache.delete(f"otp_{email}")
        return True
    return False
