def get_map_span(bounded_by: list[list[float]], margin: float = 1.2) -> tuple[str, str]:
    min_lon, min_lat = bounded_by[0]
    max_lon, max_lat = bounded_by[1]

    delta_lon = (max_lon - min_lon) * margin
    delta_lat = (max_lat - min_lat) * margin

    min_delta = 0.001
    delta_lon = max(delta_lon, min_delta)
    delta_lat = max(delta_lat, min_delta)

    return str(delta_lon), str(delta_lat)


def format_placemark(lon: str, lat: str, style: str = "pm2dgl") -> str:
    return f"{lon},{lat},{style}"