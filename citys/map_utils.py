import os
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont

STATIC_MAPS_APIKEY = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
STATIC_MAPS_URL = "https://static-maps.yandex.ru/v1"

MAPS_CACHE_DIR = "maps_cache"


def ensure_cache_dir() -> None:
    if not os.path.exists(MAPS_CACHE_DIR):
        os.makedirs(MAPS_CACHE_DIR)


def get_static_map(lon: float, lat: float, spn_lon: float, spn_lat: float,
                   size: str = "600,450", map_type: str = "map") -> bytes | None:
    params = {
        "ll": f"{lon},{lat}",
        "spn": f"{spn_lon},{spn_lat}",
        "size": size,
        "apikey": STATIC_MAPS_APIKEY,
        "l": map_type,
        "pt": f"{lon},{lat},pm2dgm"
    }

    response = requests.get(STATIC_MAPS_URL, params=params)
    if not response:
        return None

    return response.content


def save_map_image(image_bytes: bytes, filename: str) -> str:
    ensure_cache_dir()
    filepath = os.path.join(MAPS_CACHE_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(image_bytes)

    return filepath


def show_map_image(image_bytes: bytes) -> None:
    image = Image.open(BytesIO(image_bytes))
    image.show()


def add_question_number(image_bytes: bytes, question_num: int, total: int) -> bytes:
    image = Image.open(BytesIO(image_bytes))
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except Exception:
        font = ImageFont.load_default()

    text = f"Вопрос {question_num}/{total}"
    draw.text((10, 10), text, fill="white", font=font,
              stroke_width=2, stroke_fill="black")

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()