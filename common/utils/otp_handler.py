import secrets
from django.core.cache import caches

otp_handler_cache = caches['otp_handler_cache']

def generate_otp(length=6): return str(secrets.randbelow(10 * length)).zfill(length)
