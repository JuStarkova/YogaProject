import json
import os


def load_asanas():
    # путь к текущему файлу (utils)
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # поднимаемся в корень проекта (yoga_app)
    base_dir = os.path.abspath(os.path.join(current_dir, ".."))

    file_path = os.path.join(base_dir, "data", "asanas.json")


    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)