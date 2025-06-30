from django.core.cache import caches
from hashlib import sha256
from estate_data.models import EstateViews

ip_cache = caches['views_ip_cache']

def _get_key_name(ip_address):
    return f'ip_views_{sha256(ip_address.encode()).hexdigest()}'

def can_increase_views(ip_address):
    if not ip_cache.get(_get_key_name(ip_address)):
        ip_cache.set(_get_key_name(ip_address), True, timeout=3600)
        return True
    return False

def increase_views(estate, user_ip):
    if can_increase_views(user_ip):
        estate = EstateViews.objects.get(estate=estate)
        estate.views += 1
        estate.save()
