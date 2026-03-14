import math


def haversine_distance(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    R = 6371000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance


def format_distance(meters: float) -> str:
    if meters >= 1000:
        return f"{meters / 1000:.1f} км"
    else:
        return f"{meters:.0f} м"