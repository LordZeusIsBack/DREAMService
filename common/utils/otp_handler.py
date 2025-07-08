import secrets
from django.core.cache import caches
from django.core.mail import send_mail
from django.conf import settings
from hashlib import sha256
from hmac import compare_digest

otp_handler_cache = caches['default']

def _normalize_email(email):
    """
    Normalize an email address by removing leading and trailing whitespace and converting it to lowercase.
    """
    return email.strip().lower()

def hash_otp(otp):
    """
    Return the SHA-256 hexadecimal hash of the provided OTP string.

    Parameters:
	    otp (str): The OTP value to be hashed.

    Returns:
	    str: The SHA-256 hash of the OTP as a hexadecimal string.
    """
    return sha256(otp.encode()).hexdigest()

def _cache_key(prefix, email):
    """
    Generate a cache key by combining a prefix with the SHA-256 hash of the normalized email address.

    Parameters:
	    prefix (str): The cache key prefix to use.
	    email (str): The email address to be normalized and hashed.

    Returns:
	    str: The generated cache key.
    """
    return f'{prefix}_{sha256(_normalize_email(email).encode()).hexdigest()}'

def _ip_key(ip):
    """
    Generate a cache key for IP-based throttling using the provided IP address.
    """
    return f'ip_throttle{ip}'

def generate_otp(length=8):
    """
    Generate a numeric OTP of the specified length using individual random digits.

    Parameters:
        length (int): The desired length of the OTP. Defaults to 8.

    Returns:
        str: A string representing the generated OTP, padded with leading zeros if necessary.
    """
    return ''.join([str(secrets.randbelow(10)) for _ in range(length)])

def can_resend_otp(email):
    """
    Check if the OTP can be resent to the specified email based on the resend cooldown period.

    Returns:
        bool: True if the cooldown has expired and OTP can be resent, False otherwise.
    """
    return not otp_handler_cache.get(_cache_key('otp_resend', email))

def mark_otp_throttle(email, cooldown=30):
    """
    Set a throttle flag in cache for the given email to enforce a cooldown period before another OTP can be resent.

    Parameters:
	    cooldown (int): Cooldown period in seconds during which OTP resend is blocked. Defaults to 30 seconds.
    """
    otp_handler_cache.set(_cache_key('otp_resend', email), True, timeout=cooldown)

def is_otp_brute_forced(email, max_attempts=5):
    """
    Check if the number of OTP verification attempts for an email has reached or exceeded the allowed maximum.

    Returns:
        bool: True if the attempt count is greater than or equal to max_attempts, otherwise False.
    """
    return otp_handler_cache.get(_cache_key("otp_attempts", email), 0) >= max_attempts

def increment_otp_attempt(email, ttl=300):
    """
    Increment and store the OTP verification attempt count for the given email in cache.
    
    Parameters:
        email (str): The email address for which to track OTP attempts.
        ttl (int, optional): Time-to-live for the attempt count in seconds. Defaults to 300.
    
    Returns:
        int: The updated number of OTP verification attempts for the email.
    """
    key = _cache_key("otp_attempts", email)
    attempts = otp_handler_cache.get(key, 0)
    otp_handler_cache.set(key, attempts + 1, timeout=ttl)
    return attempts + 1

def clear_otp_attempts(email):
    """
    Remove the OTP attempt count for the specified email from the cache.
    """
    otp_handler_cache.delete(_cache_key("otp_attempts", email))

def is_ip_throttled(ip, max_requests=20):
    """
    Check if the number of OTP-related requests from an IP address has reached the allowed maximum.

    Returns:
        bool: True if the IP address has made at least `max_requests` requests; otherwise, False.
    """
    return otp_handler_cache.get(_ip_key(ip), 0) >= max_requests

def track_ip_request(ip, ttl=300):
    """
    Increment and store the request count for a given IP address in cache with a specified time-to-live.
    
    Parameters:
        ip (str): The IP address to track.
        ttl (int): Time-to-live for the cache entry in seconds. Defaults to 300.
    
    Returns:
        int: The updated number of requests from the IP address within the TTL window.
    """
    key = _ip_key(ip)
    count = otp_handler_cache.get(key, 0)
    otp_handler_cache.set(key, count + 1, timeout=ttl)
    return count + 1

def get_current_backoff(email):
    """
    Retrieve the current backoff timeout in seconds for OTP requests associated with the given email.

    Returns:
        int: The backoff timeout in seconds, defaulting to 30 if not set.
    """
    return otp_handler_cache.get(_cache_key("otp_backoff", email), 30)

def increase_backoff(email):
    """
    Doubles the current OTP backoff timeout for the given email, up to a maximum of 600 seconds, and stores it in cache for one hour.
    
    Returns:
        int: The updated backoff timeout in seconds.
    """
    key = _cache_key("otp_backoff", email)
    current = get_current_backoff(email)
    new_timeout = min(current * 2, 600)
    otp_handler_cache.set(key, new_timeout, timeout=3600)
    return new_timeout

def send_security_alert(email):
    """
    Send a security alert email to notify the user of suspicious OTP activity on their account.
    
    The email is sent silently; failures in sending are not raised.
    """
    send_mail(
        subject="Suspicious OTP Activity Detected",
        message=f"We noticed unusual activity with OTP submissions on your account ({email}). If this wasn't you, please contact support immediately.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=True,
    )

def send_otp(email, is_resend=False):
    """
    Sends a one-time password (OTP) to the specified email address.
    
    If `is_resend` is True, enforces a cooldown period before allowing another OTP to be sent. Generates a new OTP, stores its hash in cache with an expiration, marks the resend throttle, and sends the OTP via email. Raises a ValueError if a resend is attempted before the cooldown expires.
    
    Parameters:
        email (str): The recipient's email address.
        is_resend (bool): Whether this is a resend request. Defaults to False.
    
    Raises:
        ValueError: If a resend is attempted before the cooldown period has elapsed.
    """
    if is_resend and not can_resend_otp(email): raise ValueError('You can only resend OTP after cooldown period.')
    otp = generate_otp()
    otp_handler_cache.set(_cache_key('otp', email), hash_otp(otp), timeout=settings.OTP_TIMEOUT)

    mark_otp_throttle(email, cooldown=30)

    send_mail(
        subject="Your Verification OTP",
        message=f"Your OTP is {otp}. It is valid for {settings.OTP_TIMEOUT // 60} minutes.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )

def verify_otp(email, input_otp):
    """
    Verifies the provided OTP against the stored hashed OTP for the given email.
    
    On successful verification, clears the stored OTP and resets attempt counts. After three failed attempts, sends a security alert email to the user.
    
    Parameters:
        input_otp (str): The OTP value to verify.
    
    Returns:
        bool: True if the OTP is valid, False otherwise.
    """
    stored_otp = otp_handler_cache.get(_cache_key('otp', email))
    input_otp = hash_otp(input_otp)
    if stored_otp and compare_digest(stored_otp, input_otp):
        otp_handler_cache.delete(_cache_key('otp', email))
        clear_otp_attempts(email)
        return True
    attempts = increment_otp_attempt(email)
    if attempts == 3: send_security_alert(email)
    return False
