import random
import time
from datetime import datetime

from cities import CITIES, DIFFICULTY_LEVELS
from map_utils import (
    get_static_map,
    save_map_image,
    show_map_image,
    add_question_number,
    MAPS_CACHE_DIR
)


class GuessTheCityGame:
    def __init__(self, num_questions: int = 5, difficulty: str = "medium"):
        self.num_questions = min(num_questions, len(CITIES))
        self.difficulty = difficulty
        self.score = 0
        self.questions = []
        self.start_time = None
        self.end_time = None

        level_config = DIFFICULTY_LEVELS.get(difficulty, DIFFICULTY_LEVELS["medium"])
        self.spn_lon = level_config["spn_lon"]
        self.spn_lat = level_config["spn_lat"]

    def generate_questions(self) -> None:
        self.questions = random.sample(CITIES, self.num_questions)

    def get_map_for_city(self, city: dict, question_num: int) -> bytes | None:
        image_bytes = get_static_map(
            city["lon"],
            city["lat"],
            self.spn_lon,
            self.spn_lat
        )

        if image_bytes:
            image_bytes = add_question_number(image_bytes, question_num, self.num_questions)

        return image_bytes

    def print_header(self) -> None:
        print("ИГРА «УГАДАЙ-КА ГОРОД»")
        print(f"Количество вопросов: {self.num_questions}")
        print(f"Уровень сложности: {self.difficulty.upper()}")
        print(f"Подсказка: {DIFFICULTY_LEVELS[self.difficulty]['hint']}")

    def print_city_options(self, correct_city: dict) -> list[str]:
        other_cities = [c for c in CITIES if c["name"] != correct_city["name"]]
        wrong_cities = random.sample(other_cities, min(3, len(other_cities)))

        options = wrong_cities + [correct_city]
        random.shuffle(options)

        print("\nВарианты ответов:")
        for i, city in enumerate(options, 1):
            print(f"  {i}. {city['name']}")
        print()

        return [city["name"] for city in options]

    def play_round(self) -> None:
        self.generate_questions()
        self.start_time = datetime.now()

        for i, city in enumerate(self.questions, 1):
            print(f"ВОПРОС {i} из {self.num_questions}")

            print("Загрузка карты...")
            image_bytes = self.get_map_for_city(city, i)

            if not image_bytes:
                print("Ошибка загрузки карты, пропускаем вопрос")
                continue

            filename = f"question_{i}_{city['name']}.png"
            save_map_image(image_bytes, filename)

            print("Открываю карту...")
            show_map_image(image_bytes)

            print("\nУ вас есть 30 секунд на раздумье...")
            time.sleep(2)

            options = self.print_city_options(city)

            while True:
                try:
                    answer = input("Ваш ответ (введите номер варианта): ").strip()
                    answer_num = int(answer)

                    if 1 <= answer_num <= len(options):
                        break
                    else:
                        print(f"Введите число от 1 до {len(options)}")
                except ValueError:
                    print("Введите корректное число")

            correct_answer = city["name"]
            player_answer = options[answer_num - 1]

            if player_answer == correct_answer:
                print("✅ПРАВИЛЬНО! +1 очко")
                self.score += 1
            else:
                print(f"❌НЕПРАВИЛЬНО! Правильный ответ: {correct_answer}")

            print(f"Текущий счёт: {self.score}/{i}")

            if i < self.num_questions:
                print("\nСледующий вопрос через 3 секунды...")
                time.sleep(3)

        self.end_time = datetime.now()

    def print_results(self) -> None:
        duration = self.end_time - self.start_time
        minutes, seconds = divmod(int(duration.total_seconds()), 60)

        print("РЕЗУЛЬТАТЫ ИГРЫ")
        print(f"Правильных ответов: {self.score} из {self.num_questions}")
        print(f"Процент правильных: {self.score / self.num_questions * 100:.1f}%")
        print(f"Время игры: {minutes} мин {seconds} сек")

        percentage = self.score / self.num_questions * 100
        if percentage == 100:
            print("Оценка: ВЕЛИКОЛЕПНО! Вы знаток географии!")
        elif percentage >= 80:
            print("Оценка: ОТЛИЧНО! Хороший результат!")
        elif percentage >= 60:
            print("Оценка: ХОРОШО! Можно лучше!")
        elif percentage >= 40:
            print("Оценка: УДОВЛЕТВОРИТЕЛЬНО! Стоит повторить географию!")
        else:
            print("Оценка: НУЖНО ПОУЧИТЬСЯ! Попробуйте ещё раз!")

        print(f"Карты сохранены в папке: {MAPS_CACHE_DIR}/")


def select_difficulty() -> str:
    print("\nВыберите уровень сложности:")
    print("1. Лёгкий (easy) — маленький масштаб, видны детали")
    print("2. Средний (medium) — баланс сложности и подсказок")
    print("3. Сложный (hard) — крупный масштаб, только очертания")

    while True:
        choice = input("\nВаш выбор (1-3): ").strip()
        if choice == "1":
            print("Установлен лёгкий уровень")
            return "easy"
        elif choice == "2":
            print("Установлен средний уровень")
            return "medium"
        elif choice == "3":
            print("Установлен сложный уровень")
            return "hard"
        else:
            print("Введите число от 1 до 3")


def select_num_questions() -> int:
    print("\nВыберите количество вопросов (3-10):")

    while True:
        try:
            choice = input("Ваш выбор: ").strip()
            num = int(choice)
            if 3 <= num <= 10:
                print(f"Будет {num} вопросов")
                return num
            else:
                print("Введите число от 3 до 10")
        except ValueError:
            print("Введите корректное число")


def print_city_list() -> None:
    print("СПИСОК ГОРОДОВ В ИГРЕ")
    for i, city in enumerate(CITIES, 1):
        print(f"{i:2}. {city['name']:25} ({city['lat']:.4f}, {city['lon']:.4f})")


def main() -> None:
    print("Добро пожаловать в игру «Угадай-ка город»!")
    print("\nПравила:")
    print("Вам будет показан фрагмент карты города")
    print("Название города на карте не отображается")
    print("Выберите правильный вариант из 4 предложенных")
    print("В конце игры вы увидите свой результат")

    show_cities = input("\nПоказать список городов перед игрой? (да/нет): ").lower()
    if show_cities in ["да", "д", "yes", "y"]:
        print_city_list()

    difficulty = select_difficulty()
    num_questions = select_num_questions()

    print("НАЧИНАЕМ ИГРУ!")
    input("\nНажмите Enter, чтобы начать...")

    game = GuessTheCityGame(num_questions=num_questions, difficulty=difficulty)
    game.print_header()
    game.play_round()
    game.print_results()

    print("Спасибо за игру! До свидания!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nИгра прервана пользователем")
        print("До свидания!\n")
    except Exception as e:
        print(f"\nПроизошла ошибка: {e}")
        print("Проверьте подключение к интернету и API-ключи")
