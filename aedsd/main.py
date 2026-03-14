import sys
from io import BytesIO

import requests
from PIL import Image

from map_utils import get_map_span, format_placemark

GEOCODER_APIKEY = "8013b162-6b42-4997-9691-77b7074026e0"
STATIC_MAPS_APIKEY = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"

GEOCODER_URL = "http://geocode-maps.yandex.ru/1.x/"
STATIC_MAPS_URL = "https://static-maps.yandex.ru/v1"


def geocode(address: str) -> dict | None:
    params = {
        "apikey": GEOCODER_APIKEY,
        "geocode": address,
        "format": "json"
    }

    response = requests.get(GEOCODER_URL, params=params)
    if not response:
        return None

    json_response = response.json()
    feature_member = json_response["response"]["GeoObjectCollection"]["featureMember"]

    if not feature_member:
        return None

    return feature_member[0]["GeoObject"]


def extract_coordinates(geo_object: dict) -> tuple[str, str]:
    coords = geo_object["Point"]["pos"]
    lon, lat = coords.split(" ")
    return lon, lat


def extract_bounded_by(geo_object: dict) -> list[list[float]] | None:
    bounded_by = geo_object.get("boundedBy", {}).get("Envelope")
    if not bounded_by:
        return None

    return [
        [float(bounded_by["lowerCorner"].split()[0]), float(bounded_by["lowerCorner"].split()[1])],
        [float(bounded_by["upperCorner"].split()[0]), float(bounded_by["upperCorner"].split()[1])]
    ]


def show_on_map(lon: str, lat: str, spn_lon: str, spn_lat: str, placemark: str = None) -> None:
    map_params = {
        "ll": f"{lon},{lat}",
        "spn": f"{spn_lon},{spn_lat}",
        "apikey": STATIC_MAPS_APIKEY,
        "l": "map"
    }

    if placemark:
        map_params["pt"] = placemark

    response = requests.get(STATIC_MAPS_URL, params=map_params)
    if not response:
        return

    image = Image.open(BytesIO(response.content))
    image.show()


def main():
    address = " ".join(sys.argv[1:])

    geo_object = geocode(address)
    if not geo_object:
        return

    lon, lat = extract_coordinates(geo_object)
    print(f"Координаты: {lon}, {lat}")

    bounded_by = extract_bounded_by(geo_object)
    if bounded_by:
        spn_lon, spn_lat = get_map_span(bounded_by)
    else:
        spn_lon, spn_lat = "0.005", "0.005"

    placemark = format_placemark(lon, lat)
    show_on_map(lon, lat, spn_lon, spn_lat, placemark)


if __name__ == "__main__":
    main()