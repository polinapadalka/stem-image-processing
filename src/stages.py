"""Запуск стадій за назвою: єдине місце, де стадії з'єднано з параметрами з конфігурації."""
from src import filtering, histogram


def run_stage(name, image, params):
    """Застосовує стадію name до зображення; params - параметри цієї стадії з конфігурації."""
    if name == "bilateral":
        return filtering.bilateral_filter(
            image, params["radius"], params["sigma_space"], params["sigma_range"])
    if name == "equalize":
        return histogram.equalize_histogram(image)  # параметрів у цієї стадії немає
    # сюди додаватимемо нові стадії
    raise ValueError("Невідома стадія: " + str(name))