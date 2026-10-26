"""Запуск стадій за назвою: єдине місце, де стадії з'єднано з параметрами з конфігурації."""
from src import adaptive_filter, color, filtering, histogram, segmentation


def run_stage(name, image, params):
    """Застосовує стадію name до зображення; params - параметри цієї стадії з конфігурації."""
    if name == "bilateral":
        return filtering.bilateral_filter(
            image, params["radius"], params["sigma_space"], params["sigma_range"])
    if name == "wiener":
        return adaptive_filter.wiener_filter(image, params["radius"])
    if name == "equalize":
        return histogram.equalize_histogram(image)  # параметрів у цієї стадії немає
    if name == "saturation":
        return color.saturation_boost(image, params["factor"])
    if name == "otsu":
        return segmentation.otsu_segmentation(image)  # поріг обирається автоматично
    if name == "color_segment":
        return segmentation.color_segmentation(
            image, params["hue_min"], params["hue_max"], params["sat_min"], params["val_min"])
    # сюди додаватимемо нові стадії
    raise ValueError("Невідома стадія: " + str(name))