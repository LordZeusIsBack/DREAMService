import secrets
from django.core.cache import caches
from django.core.mail import send_mail
from django.conf import settings
from hashlib import sha256

otp_handler_cache = caches['default']

def _normalize_email(email): return email.strip().lower()

def hash_otp(otp): return sha256(otp.encode()).hexdigest()

def _cache_key(prefix, email): return f'{prefix}_{sha256(_normalize_email(email).encode()).hexdigest()}'

def _ip_key(ip): return f'ip_throttle{ip}'

def generate_otp(length=8): return str(secrets.randbelow(10 * length)).zfill(length)

def can_resend_otp(email): return not otp_handler_cache.get(_cache_key('otp_resend', email))

def mark_otp_throttle(email, cooldown=30): otp_handler_cache.set(_cache_key('otp_attempts', email), True, timeout=cooldown)

def is_otp_brute_forced(email, max_attempts=5): return otp_handler_cache.get(_cache_key("otp_attempts", email), 0) >= max_attempts

def increment_otp_attempt(email, ttl=300):
    key = _cache_key("otp_attempts", email)
    attempts = otp_handler_cache.get(key, 0)
    otp_handler_cache.set(key, attempts + 1, timeout=ttl)
    return attempts + 1

def clear_otp_attempts(email): otp_handler_cache.delete(_cache_key("otp_attempts", email))

def is_ip_throttled(ip, max_requests=20): return otp_handler_cache.get(_ip_key(ip), 0) >= max_requests

def track_ip_request(ip, ttl=300):
    key = _ip_key(ip)
    count = otp_handler_cache.get(key, 0)
    otp_handler_cache.set(key, count + 1, timeout=ttl)
    return count + 1

def get_current_backoff(email): return otp_handler_cache.get(_cache_key("otp_backoff", email), 30)

def increase_backoff(email):
    key = _cache_key("otp_backoff", email)
    current = get_current_backoff(email)
    new_timeout = min(current * 2, 600)
    otp_handler_cache.set(key, new_timeout, timeout=3600)
    return new_timeout

def send_security_alert(email):
    send_mail(
        subject="Suspicious OTP Activity Detected",
        message=f"We noticed unusual activity with OTP submissions on your account ({email}). If this wasn't you, please contact support immediately.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=True,
    )

def send_otp(email):
    otp = generate_otp()
    otp_handler_cache.set(_cache_key('otp', email), otp, timeout=settings.OTP_TIMEOUT)

    send_mail(
        subject="Your Verification OTP",
        message=f"Your OTP is {otp}. It is valid for {settings.OTP_TIMEOUT // 60} minutes.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )

def verify_otp(email, input_otp):
    stored_otp = otp_handler_cache.get(_cache_key('otp', email))
    if stored_otp and stored_otp == input_otp:
        otp_handler_cache.delete(f"otp_{email}")
        return True
    attempts = increment_otp_attempt(email)
    if attempts == 3: send_security_alert(email)
    return False
