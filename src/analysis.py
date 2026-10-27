"""Аналіз результатів: середні значення метрик за пайплайном, спотворенням і стадією."""
import csv
import math

# числові стовпці таблиці метрик
NUMBER_FIELDS = ("mse", "psnr", "ssim", "psnr_original", "ssim_original", "iou", "dice")


def read_rows(path):
    """Читає CSV із метриками; числа перетворює на float, порожні клітинки на None."""
    rows = []
    with open(path, "r", newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            for field in NUMBER_FIELDS:
                text = row.get(field)
                if text is None or text == "":
                    row[field] = None  # порожня клітинка (наприклад, IoU для не-маски)
                else:
                    row[field] = float(text)  # float("inf") теж працює
            row["stage"] = int(row["stage"])
            rows.append(row)
    return rows


def finite_values(values):
    """Лишає лише скінченні числа: None і нескінченність (однакові зображення) відкидаються."""
    result = []
    for value in values:
        if value is not None and math.isfinite(value):
            result.append(value)
    return result


def mean_std(values):
    """Повертає середнє й вибіркове стандартне відхилення; для порожнього списку (None, None)."""
    values = finite_values(values)
    if not values:
        return None, None
    mean = sum(values) / len(values)
    if len(values) == 1:  # одне значення: розкиду немає
        return mean, 0.0
    total = 0
    for value in values:
        total += (value - mean) ** 2
    return mean, (total / (len(values) - 1)) ** 0.5  # ділимо на n - 1: вибіркова оцінка


def summarize(rows):
    """Групує рядки за (пайплайн, спотворення, стадія) і рахує середні значення метрик."""
    groups = {}  # ключ - (пайплайн, спотворення, номер стадії, назва), значення - список рядків
    for row in rows:
        key = (row["pipeline"], row["degradation"], row["stage"], row["stage_name"])
        if key not in groups:
            groups[key] = []
        groups[key].append(row)
    result = []
    for key in sorted(groups):
        group = groups[key]
        item = {"pipeline": key[0], "degradation": key[1], "stage": key[2],
                "stage_name": key[3], "n": len(group)}  # n - кількість зображень у групі
        for field in NUMBER_FIELDS:
            values = []
            for row in group:
                values.append(row[field])
            mean, std = mean_std(values)
            item[field + "_mean"] = mean
            item[field + "_std"] = std
        result.append(item)
    return result