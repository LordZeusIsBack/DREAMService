from math import radians, degrees, sin, cos, asin, sqrt


def bounding_box(lat, long, radius):
    """
    Compute the minimum and maximum latitude and longitude values that define a bounding box around a geographic point.

    Parameters:
        lat (float): Latitude of the center point in decimal degrees.
        long (float): Longitude of the center point in decimal degrees.
        radius (float): Radius in kilometers from the center point.

    Returns:
        tuple: (min_lat, max_lat, min_long, max_long) representing the bounding box enclosing all points within the specified radius.
    """
    lat, long, earth_radius = float(lat), float(long), 6371
    delta_lat, delta_long = degrees(radius / earth_radius), degrees(radius / (earth_radius * cos(radians(lat))))
    return (
        lat - delta_lat,
        lat + delta_lat,
        long - delta_long,
        long + delta_long
    )


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculates the great-circle distance in kilometers between two geographic coordinates.

    Args:
        lat1: Latitude of the first point in decimal degrees.
        lon1: Longitude of the first point in decimal degrees.
        lat2: Latitude of the second point in decimal degrees.
        lon2: Longitude of the second point in decimal degrees.

    Returns:
        The distance between the two points in kilometers, computed using the haversine formula.
    """
    lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    d_lon = lon2 - lon1
    d_lat = lat2 - lat1
    a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
    return (2 * asin(sqrt(a))) * 6371
