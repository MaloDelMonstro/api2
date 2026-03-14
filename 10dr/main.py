import sys
from io import BytesIO

import requests
from PIL import Image

from map_utils import (
    get_map_span_for_points,
    format_placemark,
    get_pharmacy_style
)
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


def find_pharmacies(lon: float, lat: float, count: int = 10) -> list[dict] | None:
    params = {
        "apikey": SEARCH_APIKEY,
        "text": "аптека",
        "lang": "ru_RU",
        "ll": f"{lon},{lat}",
        "type": "biz",
        "results": str(count),
        "spn": "0.05,0.05"
    }

    response = requests.get(SEARCH_URL, params=params)

    json_response = response.json()
    features = json_response.get("features", [])

    if not features:
        return None

    return features


def extract_pharmacy_info(organization: dict, center_lon: float, center_lat: float) -> dict:
    props = organization["properties"]
    company_meta = props["CompanyMetaData"]
    geom = organization["geometry"]

    coords = geom["coordinates"]
    lon, lat = coords[0], coords[1]

    hours = company_meta.get("Hours", {})
    working_hours = hours.get("text") if hours else None

    distance_m = haversine_distance(center_lon, center_lat, lon, lat)

    return {
        "name": company_meta.get("name", "Неизвестно"),
        "address": company_meta.get("address", ""),
        "lon": lon,
        "lat": lat,
        "working_hours": working_hours,
        "distance_m": distance_m,
        "style": get_pharmacy_style(working_hours)
    }


def print_pharmacies_list(pharmacies: list[dict]) -> None:

    for i, pharmacy in enumerate(pharmacies, 1):
        color_emoji = "🟢" if pharmacy['style'] == "pm2grm" else ("🔵" if pharmacy['style'] == "pm2blm" else "⚪")
        hours_info = pharmacy['working_hours'] if pharmacy['working_hours'] else "нет данных"

        print(f"{i}. {color_emoji} {pharmacy['name']}")
        print(f"    {pharmacy['address']}")
        print(f"    {hours_info}")
        print(f"    {format_distance(pharmacy['distance_m'])}")
        print()


def show_map_with_pharmacies(pharmacies: list[dict], center_lon: float, center_lat: float) -> None:
    all_points = [(center_lon, center_lat)]
    placemarks = []

    placemarks.append(format_placemark(str(center_lon), str(center_lat), "pm2dgl"))

    for pharmacy in pharmacies:
        all_points.append((pharmacy['lon'], pharmacy['lat']))
        placemarks.append(format_placemark(
            str(pharmacy['lon']),
            str(pharmacy['lat']),
            pharmacy['style']
        ))

    center_lon_map, center_lat_map, span_lon, span_lat = get_map_span_for_points(
        all_points,
        margin=1.3
    )

    pt_param = "~".join(placemarks)

    map_params = {
        "ll": f"{center_lon_map},{center_lat_map}",
        "spn": f"{span_lon},{span_lat}",
        "apikey": STATIC_MAPS_APIKEY,
        "l": "map",
        "pt": pt_param
    }

    response = requests.get(STATIC_MAPS_URL, params=map_params)

    image = Image.open(BytesIO(response.content))
    image.show()


def main():
    address = " ".join(sys.argv[1:])

    geo_object = geocode(address)
    if not geo_object:
        return

    center_lon, center_lat = extract_coordinates(geo_object)
    normalized_address = extract_address(geo_object)
    print(f"Найдено: {normalized_address}")
    print(f"Координаты: {center_lon}, {center_lat}\n")

    pharmacies_orgs = find_pharmacies(center_lon, center_lat, count=10)
    if not pharmacies_orgs:
        return

    print(f"Найдено аптек: {len(pharmacies_orgs)}\n")

    pharmacies = []
    for org in pharmacies_orgs:
        info = extract_pharmacy_info(org, center_lon, center_lat)
        pharmacies.append(info)

    print_pharmacies_list(pharmacies)

    show_map_with_pharmacies(pharmacies, center_lon, center_lat)


if __name__ == "__main__":
    main()