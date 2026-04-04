import argparse
import requests
import sys

GEOCODER_APIKEY = "8013b162-6b42-4997-9691-77b7074026e0"
GEOCODER_URL = "http://geocode-maps.yandex.ru/1.x/"


def get_coordinates(address: str) -> tuple[str, str] | None:
    params = {
        "apikey": GEOCODER_APIKEY,
        "geocode": address,
        "format": "json",
        "results": 1,
        "lang": "ru_RU"
    }

    try:
        response = requests.get(GEOCODER_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        collection = data.get("response", {}).get("GeoObjectCollection", {})
        members = collection.get("featureMember", [])

        if not members:
            return None

        pos = members[0]["GeoObject"]["Point"]["pos"]
        lon, lat = pos.split()
        return lon, lat

    except requests.RequestException as e:
        print(f"Ошибка сети: {e}", file=sys.stderr)
        return None
    except (KeyError, IndexError, ValueError) as e:
        print(f"Ошибка парсинга ответа: {e}", file=sys.stderr)
        return None


def get_district(lon: str, lat: str) -> str | None:
    params = {
        "apikey": GEOCODER_APIKEY,
        "geocode": f"{lon},{lat}",
        "format": "json",
        "kind": "district",
        "results": 1,
        "lang": "ru_RU"
    }

    try:
        response = requests.get(GEOCODER_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        collection = data.get("response", {}).get("GeoObjectCollection", {})
        members = collection.get("featureMember", [])

        if not members:
            return None

        geo_object = members[0]["GeoObject"]
        return geo_object.get("name") or geo_object.get("description")

    except requests.RequestException as e:
        print(f"Ошибка сети при поиске района: {e}", file=sys.stderr)
        return None
    except (KeyError, IndexError):
        return None


def main():
    parser = argparse.ArgumentParser(
        description="🏙️ Определение района по адресу (Yandex Geocoder)",
        epilog='Пример: python find_district.py "Красная площадь, Москва"'
    )
    parser.add_argument(
        "address",
        nargs="+",
        help="Адрес для поиска (в кавычках, если содержит пробелы)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Показывать промежуточные данные (координаты)"
    )

    args = parser.parse_args()
    address = " ".join(args.address)

    print(f"Адрес: {address}")

    coords = get_coordinates(address)
    if not coords:
        print("Не удалось найти координаты. Проверьте адрес.")
        sys.exit(1)

    lon, lat = coords
    if args.verbose:
        print(f"Координаты: {lon}, {lat}")

    district = get_district(lon, lat)

    if district:
        print(f"Район: {district}")
    else:
        print("Район не определён")


if __name__ == "__main__":
    main()
