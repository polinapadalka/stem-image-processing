"""Графіки для звіту: стійкість масок, фільтрація, результати за класами, парні різниці."""
import csv
import os

import matplotlib
from matplotlib import pyplot

from src import analysis, comparison

matplotlib.use("Agg")  # малюємо одразу у файли, без вікон

# підписи для графіків
DEGRADATION_LABELS = {"gauss_low": "гаусів шум\n(D = 100)", "gauss_high": "гаусів шум\n(D = 900)",
                      "impulse": "імпульсний шум\n(5 %)", "haze": "серпанок\n(K = 0,5)"}
PIPELINE_LABELS = {"pipeline1": "Пайплайн 1 (поріг Оцу)",
                   "pipeline2": "Пайплайн 2 (колірна сегментація)",
                   "pipeline2m": "Пайплайн 2m (колір + морфологія)"}
SHORT_NAMES = {"pipeline1": "П1", "pipeline2": "П2", "pipeline2m": "П2m"}
COLORS = {"pipeline1": "#1f77b4", "pipeline2": "#ff7f0e", "pipeline2m": "#2ca02c"}


def summary_values(summary, pipeline, stage, field, degradations):
    """Середнє й розкид метрики за кожним спотворенням: два списки в порядку degradations."""
    means = []
    stds = []
    for key in degradations:
        found = None
        for item in summary:
            if (item["pipeline"], item["stage"], item["degradation"]) == (pipeline, stage, key):
                found = item
        mean = found[field + "_mean"] if found else None
        std = found[field + "_std"] if found else None
        means.append(mean if mean is not None else 0)
        stds.append(std if std is not None else 0)
    return means, stds


def grouped_bars(path, categories, series, ylabel, ylim=None):
    """Згруповані стовпчики з розкидом; series - список (підпис, колір, середні, розкиди)."""
    figure, axis = pyplot.subplots(figsize=(8, 4.5))
    width = 0.8 / len(series)
    for index, (label, color, means, stds) in enumerate(series):
        shift = (index - (len(series) - 1) / 2) * width
        positions = [i + shift for i in range(len(categories))]
        axis.bar(positions, means, width, yerr=stds, capsize=3, label=label, color=color)
    axis.set_xticks(range(len(categories)))
    axis.set_xticklabels(categories)
    axis.set_ylabel(ylabel)
    if ylim:
        axis.set_ylim(*ylim)
    axis.grid(axis="y", alpha=0.3)
    figure.legend(loc="lower center", ncol=len(series), fontsize=8)  # легенда під графіком
    figure.tight_layout(rect=(0, 0.07, 1, 1))
    figure.savefig(path, dpi=200)
    pyplot.close(figure)


def class_bars(path, class_values, names, xlabel):
    """Горизонтальні стовпчики за класами; class_values[ім'я пайплайна] = {клас: середнє}."""
    classes = sorted(class_values[names[0]])
    figure, axis = pyplot.subplots(figsize=(8, 5))
    width = 0.8 / len(names)
    for index, name in enumerate(names):
        shift = (index - (len(names) - 1) / 2) * width
        positions = [i + shift for i in range(len(classes))]
        values = [class_values[name].get(class_, 0) for class_ in classes]
        axis.barh(positions, values, width, label=PIPELINE_LABELS.get(name, name),
                  color=COLORS.get(name))
    axis.set_yticks(range(len(classes)))
    axis.set_yticklabels(classes)
    axis.invert_yaxis()
    axis.set_xlabel(xlabel)
    axis.set_xlim(0, 1.05)
    axis.grid(axis="x", alpha=0.3)
    figure.legend(loc="lower center", ncol=len(names), fontsize=8)  # легенда під графіком
    figure.tight_layout(rect=(0, 0.06, 1, 1))
    figure.savefig(path, dpi=200)
    pyplot.close(figure)


def read_paired(path):
    """Читає таблицю парних порівнянь (результат команди analyze)."""
    items = []
    with open(path, "r", newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            for field in ("mean", "low", "high"):
                row[field] = float(row[field])
            items.append(row)
    return items


def paired_items(items, field, degradations):
    """Вибирає рядки парних порівнянь для метрики й повертає (підпис, середнє, низ, верх)."""
    result = []
    for item in items:
        if item["field"] != field or item["degradation"] not in degradations:
            continue
        degradation = DEGRADATION_LABELS.get(item["degradation"], item["degradation"])
        label = (SHORT_NAMES.get(item["b"], item["b"]) + " - " +
                 SHORT_NAMES.get(item["a"], item["a"]) + ", " + degradation.replace("\n", " "))
        result.append((label, item["mean"], item["low"], item["high"]))
    return result


def paired_plot(path, points, xlabel):
    """Різниці метрик із 95 % інтервалами; нуль (немає різниці) позначено вертикальною лінією."""
    figure, axis = pyplot.subplots(figsize=(8, 0.55 * len(points) + 1.6))
    for position, (_, mean, low, high) in enumerate(points):
        axis.plot([low, high], [position, position], color="#444444", linewidth=2)
        axis.plot([mean], [position], "o", color="#d62728")
    axis.axvline(0, color="black", linewidth=1)
    axis.set_yticks(range(len(points)))
    axis.set_yticklabels([point[0] for point in points], fontsize=8)
    axis.invert_yaxis()
    axis.set_xlabel(xlabel)
    axis.grid(axis="x", alpha=0.3)
    figure.tight_layout()
    figure.savefig(path, dpi=200)
    pyplot.close(figure)


def make_all(config, rows):
    """Створює всі графіки в results/figures за таблицями метрик усіх пайплайнів."""
    folder = os.path.join(config["paths"]["results"], "figures")
    os.makedirs(folder, exist_ok=True)
    degradations = list(config["degradations"])
    categories = [DEGRADATION_LABELS.get(key, key) for key in degradations]
    names = []
    last = {}
    for name in config["pipelines"]:
        if comparison.select(rows, name, 1):
            names.append(name)
            last[name] = len(config["pipelines"][name])
    summary = analysis.summarize(rows)

    # 1. стійкість масок
    series = []
    for name in names:
        means, stds = summary_values(summary, name, last[name], "iou", degradations)
        series.append((PIPELINE_LABELS.get(name, name), COLORS.get(name), means, stds))
    grouped_bars(os.path.join(folder, "fig_mask_iou.png"), categories, series,
                 "середній IoU з маскою чистого знімка", (0, 1.05))

    # 2. якість фільтрації на стадії 1 (PSNR відносно чистого оригіналу)
    series = []
    for name in names:
        means, stds = summary_values(summary, name, 1, "psnr_original", degradations)
        series.append((PIPELINE_LABELS.get(name, name), COLORS.get(name), means, stds))
    grouped_bars(os.path.join(folder, "fig_stage1_psnr.png"), categories, series,
                 "середній PSNR стадії 1 відносно оригіналу, дБ")

    # 3. результати за класами знімків
    class_values = {}
    for name in names:
        by_class = comparison.by_class(rows, name, last[name], "iou")
        class_values[name] = {class_: value[0] for class_, value in by_class.items()}
    class_bars(os.path.join(folder, "fig_iou_by_class.png"), class_values, names,
               "середній IoU маски (усі спотворення)")

    # 4. парні різниці з довірчими інтервалами
    paired_path = os.path.join(config["paths"]["results"], "paired_comparisons.csv")
    if os.path.exists(paired_path):
        items = read_paired(paired_path)
        paired_plot(os.path.join(folder, "fig_paired_iou.png"),
                    paired_items(items, "iou", degradations),
                    "різниця IoU (b - a) з 95 % інтервалом")
        paired_plot(os.path.join(folder, "fig_paired_psnr.png"),
                    paired_items(items, "psnr_original", degradations),
                    "різниця PSNR стадії 1 (b - a), дБ, з 95 % інтервалом")
    else:
        print("Немає results/paired_comparisons.csv: спочатку виконай analyze")
    print("Графіки збережено в", folder)