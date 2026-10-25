"""Точка входу STEM-проєкту: підготовка вибірки, спотворення, метрики."""

# argparse - стандартна бібліотека для аргументів командного рядка
import argparse
import json  # для читання файлу конфігурації
import os
import random

from src import degrade, image_io, metrics, results_io


def load_config(path):
    """Читає параметри з JSON-файлу, щоб їх можна було міняти без правки коду."""
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def command_prepare(config):
    """Готує вибірку: квадрат із центру, зменшення до image_size, збереження у PNG."""
    saved = 0  # лічильник підготовлених зображень
    for path in image_io.list_images(config["paths"]["original"]):
        image = image_io.load_image(path)
        if image is None:  # файл пошкоджений або порожній: пропускаємо його, а не падаємо
            print("Пропущено (файл пошкоджений або порожній):", path)
            continue
        small = image_io.square_resize(image, config["image_size"])
        name = os.path.splitext(os.path.basename(path))[0]  # назва файлу без розширення
        image_io.save_image(small, os.path.join(config["paths"]["prepared"], name + ".png"))
        saved += 1
    if saved == 0:
        print("Немає зображень у папці", config["paths"]["original"])
    else:
        print("Підготовлено зображень:", saved)


def command_degrade(config):
    """Створює спотворені копії кожного підготовленого зображення й зберігає їхні метрики."""
    rows = []  # рядки майбутньої таблиці результатів
    window = config["metrics"]["ssim_window"]  # параметри SSIM з конфігурації
    step = config["metrics"]["ssim_step"]
    for path in image_io.list_images(config["paths"]["prepared"]):
        clean = image_io.load_image(path)  # чисте зображення: еталон
        if clean is None:
            print("Пропущено:", path)
            continue
        name = os.path.splitext(os.path.basename(path))[0]
        for key, spec in config["degradations"].items():  # key - назва, spec - параметри
            # для кожної пари "зображення + спотворення" свій, але завжди той самий seed
            rng = random.Random(str(config["seed"]) + name + key)
            noisy = degrade.apply_degradation(clean, spec, rng)
            out_path = os.path.join(config["paths"]["degraded"], name + "__" + key + ".png")
            image_io.save_image(noisy, out_path)
            row = {"image": name, "degradation": key}  # початок рядка таблиці
            row.update(metrics.compare(clean, noisy, window, step))  # додаємо MSE, PSNR, SSIM
            rows.append(row)
            print(name, key, "PSNR =", round(row["psnr"], 2))
    if not rows:
        print("Немає підготовлених зображень: спочатку виконай команду prepare")
        return
    results_io.write_csv(
        os.path.join(config["paths"]["results"], "degradation_metrics.csv"),
        rows, ["image", "degradation", "mse", "psnr", "ssim"])


def command_metrics(config, path_a, path_b):
    """Виводить MSE, PSNR і SSIM для двох файлів."""
    image_a = image_io.load_image(path_a)
    image_b = image_io.load_image(path_b)
    if image_a is None or image_b is None:
        print("Не вдалося відкрити одне із зображень")
        return
    if image_a.size != image_b.size:  # порівнювати можна лише однакові розміри
        print("Розміри зображень різні:", image_a.size, image_b.size)
        return
    result = metrics.compare(image_a, image_b, config["metrics"]["ssim_window"],
                             config["metrics"]["ssim_step"])
    for name, value in result.items():
        print(name.upper(), "=", round(value, 4))


def main():
    """Розбирає аргументи командного рядка й запускає потрібну команду."""
    parser = argparse.ArgumentParser(description="STEM-проєкт: обробка зображень")
    parser.add_argument("--config", default="config.json", help="шлях до файлу конфігурації")
    # підкоманди: prepare, degrade, metrics
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("prepare", help="підготувати вибірку зображень")
    subparsers.add_parser("degrade", help="створити спотворені копії")
    metrics_parser = subparsers.add_parser("metrics", help="порахувати метрики для двох файлів")
    metrics_parser.add_argument("image_a")  # перший файл
    metrics_parser.add_argument("image_b")  # другий файл
    args = parser.parse_args()  # argparse читає те, що написано в командному рядку

    try:
        config = load_config(args.config)
    except (OSError, ValueError):  # немає файлу або в ньому помилка JSON
        print("Не вдалося прочитати файл конфігурації:", args.config)
        return

    if args.command == "prepare":
        command_prepare(config)
    elif args.command == "degrade":
        command_degrade(config)
    else:
        command_metrics(config, args.image_a, args.image_b)


if __name__ == "__main__":
    main()