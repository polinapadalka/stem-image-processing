"""Перевірка еталонних сценаріїв коректності: чи виконуються пороги з config.json."""
import csv

from src import analysis, comparison


def read_degraded(path):
    """Читає таблицю метрик спотворених знімків (стовпці image, degradation, psnr)."""
    rows = []
    with open(path, "r", newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            row["psnr"] = float(row["psnr"])
            rows.append(row)
    return rows


def gain_count(selected, degraded_rows, degradation, min_gain):
    """Рахує знімки, у яких PSNR після стадії вищий за PSNR спотвореного не менш ніж на min_gain."""
    before_psnr = {}  # знімок -> PSNR спотвореної копії відносно чистого знімка
    for row in degraded_rows:
        if row["degradation"] == degradation:
            before_psnr[row["image"]] = row["psnr"]
    passed = 0
    total = 0
    for row in selected:
        before = before_psnr.get(row["image"])
        after = row["psnr_original"]
        if before is None or after is None:  # немає даних для цього знімка
            continue
        total += 1
        if after - before >= min_gain:
            passed += 1
    return passed, total


def run_scenarios(rows, degraded_rows, scenarios, last_stage, degradations):
    """Перевіряє кожен сценарій для кожного пайплайна; повертає список тест-кейсів."""
    cases = []
    for scenario in scenarios:
        for name in scenario["pipelines"]:
            if scenario["kind"] == "gain":
                key = scenario["degradation"]
                selected = comparison.select(rows, name, 1, key)
                passed, total = gain_count(selected, degraded_rows, key, scenario["min_gain"])
                value = passed / total if total else 0
                cases.append({"id": scenario["id"], "pipeline": name, "degradation": key,
                              "value": value, "required": scenario["min_share"],
                              "ok": total > 0 and value >= scenario["min_share"],
                              "note": "частка знімків із приростом PSNR не менше " +
                                      str(scenario["min_gain"]) + " дБ"})
            else:
                for key in degradations:
                    selected = comparison.select(rows, name, last_stage[name], key)
                    values = []
                    for row in selected:
                        values.append(row[scenario["field"]])
                    mean, _ = analysis.mean_std(values)
                    cases.append({"id": scenario["id"], "pipeline": name, "degradation": key,
                                  "value": mean, "required": scenario["min_mean"],
                                  "ok": mean is not None and mean >= scenario["min_mean"],
                                  "note": "середнє значення " + scenario["field"]})
    return cases


def count_passed(cases):
    """Повертає кількість пройдених тест-кейсів і загальну кількість."""
    passed = 0
    for case in cases:
        if case["ok"]:
            passed += 1
    return passed, len(cases)