"""Порівняння пайплайнів: за класами знімків і парне порівняння по однакових знімках."""
import math

from src import analysis

Z = 1.96  # множник для 95 % довірчого інтервалу (нормальне наближення)


def class_name(image_name):
    """Назва класу зі знімка: forest05 -> forest."""
    return image_name[:-2]


def select(rows, pipeline, stage, degradation=None):
    """Вибирає рядки таблиці для пайплайна й номера стадії (і, за потреби, для спотворення)."""
    result = []
    for row in rows:
        if row["pipeline"] != pipeline or row["stage"] != stage:
            continue
        if degradation is not None and row["degradation"] != degradation:
            continue
        result.append(row)
    return result


def by_class(rows, pipeline, stage, field, degradation=None):
    """Середнє значення метрики за класами: повертає словник {клас: (середнє, кількість)}."""
    groups = {}
    for row in select(rows, pipeline, stage, degradation):
        name = class_name(row["image"])
        if name not in groups:
            groups[name] = []
        groups[name].append(row[field])
    result = {}
    for name, values in groups.items():
        mean, _ = analysis.mean_std(values)
        result[name] = (mean, len(analysis.finite_values(values)))
    return result


def paired(rows_a, rows_b, field):
    """Парне порівняння по однакових знімках: різниця b - a, 95 % інтервал, частка перемог b."""
    values_a = {}
    for row in rows_a:
        values_a[row["image"]] = row[field]
    differences = []
    for row in rows_b:
        value_a = values_a.get(row["image"])
        value_b = row[field]
        if value_a is None or value_b is None:  # немає значення для цього знімка
            continue
        if math.isfinite(value_a) and math.isfinite(value_b):
            differences.append(value_b - value_a)
    count = len(differences)
    if count == 0:
        return None
    mean, std = analysis.mean_std(differences)
    margin = Z * std / math.sqrt(count)  # половина довжини довірчого інтервалу
    wins = 0
    for difference in differences:
        if difference > 0:
            wins += 1
    return {"n": count, "mean": mean, "low": mean - margin, "high": mean + margin,
            "wins": wins / count}
