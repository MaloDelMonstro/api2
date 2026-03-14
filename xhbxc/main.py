import sys
from io import BytesIO

import requests
from PIL import Image

from map_utils import get_map_span_for_two_points, format_placemark
from distance_utils import haversine_distance, format_distance

GEOCODER_APIKEY = "8013b162-6b42-4997-9691-77b7074026e0"
STATIC_MAPS_APIKEY = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
SEARCH_APIKEY = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

GEOCODER_URL = "http://geocode-maps.yandex.ru/1.x/"
STATIC_MAPS_URL = "https://static-maps.yandex.ru/v1"
SEARCH_URL = "https://search-maps.yandex.ru/v1/"


def geocode(address: str) -> dict | None:
    params = {
        "apikey": GEOCODER_APIKEY,
        "geocode": address,
        "format": "json"
    }

    response = requests.get(GEOCODER_URL, params=params)

    json_response = response.json()
    feature_member = json_response["response"]["GeoObjectCollection"]["featureMember"]

    return feature_member[0]["GeoObject"]


def extract_coordinates(geo_object: dict) -> tuple[float, float]:
    coords = geo_object["Point"]["pos"]
    lon, lat = map(float, coords.split(" "))
    return lon, lat


def extract_address(geo_object: dict) -> str:
    return geo_object["metaDataProperty"]["GeocoderMetaData"]["text"]


def find_nearest_pharmacy(lon: float, lat: float) -> dict | None:
    params = {
        "apikey": SEARCH_APIKEY,
        "text": "аптека",
        "lang": "ru_RU",
        "ll": f"{lon},{lat}",
        "type": "biz",
        "results": "1"
    }

    response = requests.get(SEARCH_URL, params=params)

    json_response = response.json()
    features = json_response.get("features", [])

    if not features:
        return None

    return features[0]


def extract_pharmacy_info(organization: dict) -> dict:

    props = organization["properties"]
    company_meta = props["CompanyMetaData"]
    geom = organization["geometry"]

    coords = geom["coordinates"]
    lon, lat = coords[0], coords[1]


    return {
        "name": company_meta.get("name", "Неизвестно"),
        "address": company_meta.get("address", ""),
        "lon": lon,
        "lat": lat,
    }


def print_snippet(address: str, pharmacy: dict, distance_m: float) -> None:
    distance_str = format_distance(distance_m)

    print(f"Исходный адрес:    {address}")
    print(f"Адрес аптеки:      {pharmacy['address']}")
    print(f"Расстояние:        {distance_str}")


def show_map_with_points(start_lon: float, start_lat: float,
                         pharmacy_lon: float, pharmacy_lat: float) -> None:
    center_lon, center_lat, span_lon, span_lat = get_map_span_for_two_points(
        (start_lon, start_lat),
        (pharmacy_lon, pharmacy_lat),
        margin=1.5
    )

    placemark_start = format_placemark(str(start_lon), str(start_lat), "pm2blm")
    placemark_pharmacy = format_placemark(str(pharmacy_lon), str(pharmacy_lat), "pm2dgl")

    pt_param = f"{placemark_start}~{placemark_pharmacy}"

    map_params = {
        "ll": f"{center_lon},{center_lat}",
        "spn": f"{span_lon},{span_lat}",
        "apikey": STATIC_MAPS_APIKEY,
        "l": "map",
        "pt": pt_param
    }

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

    start_lon, start_lat = extract_coordinates(geo_object)
    normalized_address = extract_address(geo_object)
    print(f"Найдено: {normalized_address}")
    print(f"Координаты: {start_lon}, {start_lat}\n")

    pharmacy_org = find_nearest_pharmacy(start_lon, start_lat)
    if not pharmacy_org:
        return

    pharmacy_info = extract_pharmacy_info(pharmacy_org)

    distance_m = haversine_distance(
        start_lon, start_lat,
        pharmacy_info['lon'], pharmacy_info['lat']
    )

    print_snippet(normalized_address, pharmacy_info, distance_m)

    show_map_with_points(start_lon, start_lat, pharmacy_info['lon'], pharmacy_info['lat'])


if __name__ == "__main__":
    main()