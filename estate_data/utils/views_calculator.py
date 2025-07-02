from django.core.cache import caches
from django.db.models import F
from hashlib import sha256
from estate_data.models import EstateMetrics

ip_cache = caches['views_ip_cache']

def _get_key_name(ip_address):
    """
    Generate a cache key for an IP address by hashing it with SHA-256 and prefixing with 'ip_views_'.
    
    Parameters:
        ip_address (str): The IP address to be hashed.
    
    Returns:
        str: The generated cache key for tracking views by this IP address.
    """
    return f'ip_views_{sha256(ip_address.encode()).hexdigest()}'

def can_increase_views(ip_address):
    """
    Determine whether the given IP address is eligible to increment the view count.
    
    Returns:
        bool: True if the IP address has not recently increased the view count (within the last hour); False otherwise.
    """
    if not ip_cache.get(_get_key_name(ip_address)):
        ip_cache.set(_get_key_name(ip_address), True, timeout=3600)
        return True
    return False

def increase_views(estate, user_ip):
    """
    Increments the view count for an estate if the user's IP address has not recently contributed to the count.
    
    Parameters:
        estate: The estate object whose views are being tracked.
        user_ip (str): The IP address of the user attempting to increase the view count.
    """
    if can_increase_views(user_ip):
        EstateMetrics.objects.filter(estate=estate).update(views=F('views') + 1)
