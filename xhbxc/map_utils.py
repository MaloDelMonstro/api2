def get_map_span(bounded_by: list[list[float]], margin: float = 1.2) -> tuple[str, str]:
    min_lon, min_lat = bounded_by[0]
    max_lon, max_lat = bounded_by[1]

    delta_lon = (max_lon - min_lon) * margin
    delta_lat = (max_lat - min_lat) * margin

    min_delta = 0.001
    delta_lon = max(delta_lon, min_delta)
    delta_lat = max(delta_lat, min_delta)

    return str(delta_lon), str(delta_lat)


def get_map_span_for_two_points(point1: tuple[float, float],
                                 point2: tuple[float, float],
                                 margin: float = 1.5) -> tuple[str, str, str, str]:
    lon1, lat1 = point1
    lon2, lat2 = point2

    center_lon = (lon1 + lon2) / 2
    center_lat = (lat1 + lat2) / 2

    min_lon = min(lon1, lon2)
    min_lat = min(lat1, lat2)
    max_lon = max(lon1, lon2)
    max_lat = max(lat1, lat2)

    bounded_by = [[min_lon, min_lat], [max_lon, max_lat]]
    span_lon, span_lat = get_map_span(bounded_by, margin)

    return str(center_lon), str(center_lat), span_lon, span_lat


def format_placemark(lon: str, lat: str, style: str = "pm2dgl") -> str:
    return f"{lon},{lat},{style}"