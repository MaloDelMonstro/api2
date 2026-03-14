import os
import threading
import time
import webbrowser
from urllib.parse import unquote

from flask import Flask, render_template

PROJECT_DIR = ""
TEMPLATES_FOLDER = os.path.join(PROJECT_DIR, "templates")

app = Flask(__name__, template_folder=TEMPLATES_FOLDER)


@app.route('/', defaults={'page_title': 'Главная'})
@app.route('/<path:page_title>')
def index(page_title: str) -> str:
    decoded_title = unquote(page_title)
    return render_template('index.html', title=decoded_title)


@app.route('/index')
@app.route('/index/<path:page_title>')
def index_alias(page_title='Главная') -> str:
    decoded_title = unquote(page_title)
    return render_template('index.html', title=decoded_title)


def open_browser() -> None:
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:8080/Подготовка%20к%20миссии")


if __name__ == '__main__':
    # Создаём структуру папок, если нет
    if not os.path.exists(TEMPLATES_FOLDER):
        os.makedirs(TEMPLATES_FOLDER)

    # Запускаем браузер в отдельном потоке
    threading.Thread(target=open_browser, daemon=True).start()

    # Запускаем сервер
    app.run(debug=False, port=8080)