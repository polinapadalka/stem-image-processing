"""Точка входу STEM-проєкту: підготовка вибірки, спотворення, метрики."""
# argparse - стандартна бібліотека для аргументів командного рядка
import argparse
import json  # для читання файлу конфігурації
import os
import random

from src import degrade, image_io, metrics, pipelines, results_io, stages


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


def command_stage(config, name, path_in, path_out, path_reference):
    """Застосовує одну стадію до файлу; якщо є еталон, друкує метрики до і після."""
    image = image_io.load_image(path_in)
    if image is None:
        print("Не вдалося відкрити зображення:", path_in)
        return
    try:
        # параметри стадії беремо з config.json; get повертає {}, якщо розділу немає
        result = stages.run_stage(name, image, config["stages"].get(name, {}))
    except ValueError as error:  # невідома назва стадії
        print(error)
        return
    image_io.save_image(result, path_out)
    print("Збережено:", path_out)
    if path_reference:  # якщо вказано чисте зображення, рахуємо метрики
        reference = image_io.load_image(path_reference)
        if reference is None or reference.size != image.size:
            print("Еталон не відкрито або його розмір інший: метрики пропущено")
            return
        window = config["metrics"]["ssim_window"]
        step = config["metrics"]["ssim_step"]
        for label, current in (("до", image), ("після", result)):
            values = metrics.compare(reference, current, window, step)
            print(label, {key: round(value, 4) for key, value in values.items()})


def command_run(config, pipeline_name):
    """Проганяє пайплайн по всіх підготовлених зображеннях і їхніх спотворених копіях."""
    if pipeline_name not in config["pipelines"]:
        print("Невідомий пайплайн:", pipeline_name)
        return
    stage_names = config["pipelines"][pipeline_name]  # список стадій, наприклад bilateral, ...
    window = config["metrics"]["ssim_window"]
    step = config["metrics"]["ssim_step"]
    out_folder = os.path.join(config["paths"]["results"], pipeline_name)  # куди класти картинки
    rows = []  # рядки таблиці метрик
    try:
        for path in image_io.list_images(config["paths"]["prepared"]):
            clean = image_io.load_image(path)
            if clean is None:
                print("Пропущено:", path)
                continue
            name = os.path.splitext(os.path.basename(path))[0]
            # еталон: ті самі стадії, застосовані до чистого зображення
            reference_outputs = pipelines.run_chain(clean, stage_names, config["stages"])
            if config["save_intermediate"]:
                save_outputs(reference_outputs, stage_names, out_folder, name + "__clean")
            for key in config["degradations"]:
                noisy_path = os.path.join(config["paths"]["degraded"], name + "__" + key + ".png")
                noisy = image_io.load_image(noisy_path)
                if noisy is None:
                    print("Немає спотвореної копії (спочатку виконай degrade):", noisy_path)
                    continue
                outputs = pipelines.run_chain(noisy, stage_names, config["stages"])
                if config["save_intermediate"]:
                    save_outputs(outputs, stage_names, out_folder, name + "__" + key)
                stage_rows = pipelines.evaluate_chain(
                    clean, reference_outputs, outputs, stage_names, window, step)
                for row in stage_rows:
                    full_row = {"pipeline": pipeline_name, "image": name, "degradation": key}
                    full_row.update(row)  # додаємо номер стадії та метрики
                    rows.append(full_row)
                print(name, key, "SSIM кінцевої стадії =", round(stage_rows[-1]["ssim"], 4))
    except ValueError as error:  # невідома назва стадії в конфігурації
        print(error)
        return
    if not rows:
        print("Немає даних: спочатку виконай prepare і degrade")
        return
    fields = ["pipeline", "image", "degradation", "stage", "stage_name", "mse", "psnr",
              "ssim", "psnr_original", "ssim_original", "iou", "dice"]
    csv_path = os.path.join(config["paths"]["results"], pipeline_name + "_metrics.csv")
    results_io.write_csv(csv_path, rows, fields)
    print("Таблицю метрик збережено:", csv_path)


def save_outputs(outputs, stage_names, folder, prefix):
    """Зберігає проміжні результати стадій як prefix__1_назва.png, prefix__2_назва.png..."""
    for index, image in enumerate(outputs):
        file_name = prefix + "__" + str(index + 1) + "_" + stage_names[index] + ".png"
        image_io.save_image(image, os.path.join(folder, file_name))


def main():
    """Розбирає аргументи командного рядка й запускає потрібну команду."""
    parser = argparse.ArgumentParser(description="STEM-проєкт: обробка зображень")
    parser.add_argument("--config", default="config.json", help="шлях до файлу конфігурації")
    # підкоманди: prepare, degrade, metrics, stage, run
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("prepare", help="підготувати вибірку зображень")
    subparsers.add_parser("degrade", help="створити спотворені копії")
    metrics_parser = subparsers.add_parser("metrics", help="порахувати метрики для двох файлів")
    metrics_parser.add_argument("image_a")  # перший файл
    metrics_parser.add_argument("image_b")  # другий файл
    stage_parser = subparsers.add_parser("stage", help="застосувати одну стадію до файлу")
    stage_parser.add_argument("name", help="назва стадії, наприклад bilateral")
    stage_parser.add_argument("path_in")  # що обробляємо
    stage_parser.add_argument("path_out")  # куди зберегти результат
    stage_parser.add_argument("--reference", default=None, help="чисте зображення для метрик")
    run_parser = subparsers.add_parser("run", help="запустити пайплайн на всій вибірці")
    run_parser.add_argument("pipeline", help="назва пайплайна з config.json")
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
    elif args.command == "run":
        command_run(config, args.pipeline)
    elif args.command == "stage":
        command_stage(config, args.name, args.path_in, args.path_out, args.reference)
    else:
        command_metrics(config, args.image_a, args.image_b)


if __name__ == "__main__":
    main()