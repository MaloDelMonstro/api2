def get_map_span(bounded_by: list[list[float]], margin: float = 1.2) -> tuple[str, str]:
    min_lon, min_lat = bounded_by[0]
    max_lon, max_lat = bounded_by[1]

    delta_lon = (max_lon - min_lon) * margin
    delta_lat = (max_lat - min_lat) * margin

    min_delta = 0.001
    delta_lon = max(delta_lon, min_delta)
    delta_lat = max(delta_lat, min_delta)

    return str(delta_lon), str(delta_lat)


def get_map_span_for_points(points: list[tuple[float, float]],
                            margin: float = 1.3) -> tuple[str, str, str, str]:
    if not points:
        return "0", "0", "0.01", "0.01"

    lons = [p[0] for p in points]
    lats = [p[1] for p in points]

    center_lon = sum(lons) / len(lons)
    center_lat = sum(lats) / len(lats)

    min_lon = min(lons)
    min_lat = min(lats)
    max_lon = max(lons)
    max_lat = max(lats)

    bounded_by = [[min_lon, min_lat], [max_lon, max_lat]]
    span_lon, span_lat = get_map_span(bounded_by, margin)

    return str(center_lon), str(center_lat), span_lon, span_lat


def format_placemark(lon: str, lat: str, style: str = "pm2dgl") -> str:
    return f"{lon},{lat},{style}"


def get_pharmacy_style(working_hours: str | None) -> str:
    if working_hours is None:
        return "pm2sml"

    hours_lower = working_hours.lower()
    if "круглосуточно" in hours_lower or "24" in hours_lower:
        return "pm2grm"
    else:
        return "pm2blm"