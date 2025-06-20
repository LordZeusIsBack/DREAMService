import secrets
from django.core.cache import caches
from django.core.mail import send_mail
from django.conf import settings
from hashlib import sha256

otp_handler_cache = caches['otp_handler_cache']

def _normalize_email(email): return email.strip().lower()

def _cache_key(prefix, email): return f'{prefix}_{sha256(email.encode()).hexdigest()}'

def _ip_key(ip): return f'ip_throttle{ip}'

def generate_otp(length=6): return str(secrets.randbelow(10 * length)).zfill(length)

def can_resend_otp(email): return not otp_handler_cache.get(_cache_key('otp_resend', email))

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
