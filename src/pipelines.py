"""Пайплайни: послідовність стадій та оцінка результатів кожної стадії."""
from src import mask_metrics, metrics, stages

# стадії, які повертають чорно-білу маску: для них додатково рахуємо IoU і Дайса
MASK_STAGES = ("otsu", "color_segment", "morphology")


def run_chain(image, stage_names, stage_params):
    """Послідовно застосовує стадії до зображення; повертає результати після кожної стадії."""
    outputs = []  # результати стадій: outputs[0] - після першої, outputs[1] - після другої...
    current = image  # те, що подаємо на вхід наступній стадії
    for name in stage_names:
        # параметри стадії беремо з конфігурації; get повертає {}, якщо їх там немає
        current = stages.run_stage(name, current, stage_params.get(name, {}))
        outputs.append(current)
    return outputs


def evaluate_chain(clean, reference_outputs, outputs, stage_names, window, step):
    """Порівнює результати кожної стадії з еталонними й повертає рядки таблиці метрик.
    reference_outputs - результати тих самих стадій на чистому зображенні (еталон стадії),
    outputs - результати на спотвореному зображенні, clean - чисте початкове зображення.
    """
    rows = []
    for index, name in enumerate(stage_names):
        row = {"stage": index + 1, "stage_name": name}  # номер стадії рахуємо з 1
        # метрики відносно еталонного результату стадії
        row.update(metrics.compare(reference_outputs[index], outputs[index], window, step))
        # метрики відносно чистого початкового зображення (корисно для стадій відновлення)
        original = metrics.compare(clean, outputs[index], window, step)
        row["psnr_original"] = original["psnr"]
        row["ssim_original"] = original["ssim"]
        if name in MASK_STAGES:  # для масок додаємо IoU і Дайса
            row["iou"] = mask_metrics.iou(reference_outputs[index], outputs[index])
            row["dice"] = mask_metrics.dice(reference_outputs[index], outputs[index])
        else:  # для звичайних зображень ці метрики не мають сенсу
            row["iou"] = ""
            row["dice"] = ""
        rows.append(row)
    return rows
