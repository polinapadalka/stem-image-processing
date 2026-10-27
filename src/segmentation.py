"""Сегментація: поділ зображення на об'єкт і фон (стадії 3 пайплайнів 1 і 2)."""
from src import color, histogram


def otsu_threshold(image):
    """Знаходить поріг яскравості, який найкраще ділить пікселі на дві групи (метод Оцу)."""
    levels = histogram.brightness_levels(image)  # яскравість кожного пікселя
    counts = [0] * 256  # гістограма: скільки пікселів має кожну яскравість
    for row in levels:
        for level in row:
            counts[level] += 1

    pixel_count = 0  # загальна кількість пікселів
    total_sum = 0  # сума яскравостей усіх пікселів
    for i in range(256):
        pixel_count += counts[i]
        total_sum += i * counts[i]

    best_threshold = 255  # якщо поділити не можна (однотонне зображення), усе буде фоном
    best_variance = -1  # найбільша міжкласова дисперсія, знайдена досі
    dark_count = 0  # w0: скільки пікселів не світліші за поріг
    dark_sum = 0  # сума яскравостей цих пікселів
    for t in range(256):  # перебираємо всі можливі пороги
        dark_count += counts[t]
        dark_sum += t * counts[t]
        light_count = pixel_count - dark_count  # w1: скільки пікселів світліші за поріг
        if dark_count == 0 or light_count == 0:  # одна з груп порожня: поділу немає
            continue
        mean_dark = dark_sum / dark_count  # середня яскравість темної групи
        mean_light = (total_sum - dark_sum) / light_count  # середня яскравість світлої групи
        variance = dark_count * light_count * (mean_dark - mean_light) ** 2
        if variance > best_variance:  # строго більше: при рівності лишається менший поріг
            best_variance = variance
            best_threshold = t
    return best_threshold


def otsu_segmentation(image):
    """Повертає чорно-біле зображення: світліші за поріг Оцу пікселі білі, решта чорні."""
    threshold = otsu_threshold(image)
    levels = histogram.brightness_levels(image)
    width, height = image.size
    result = image.copy()
    pixels = result.load()
    for y in range(height):
        for x in range(width):
            if levels[y][x] > threshold:  # світліше за поріг: об'єкт
                pixels[x, y] = (255, 255, 255)
            else:  # не світліше за поріг: фон
                pixels[x, y] = (0, 0, 0)
    return result


def color_segmentation(image, hue_min, hue_max, sat_min, val_min):
    """Колірна сегментація: білі пікселі із заданим відтінком, насиченістю й яскравістю."""
    result = image.copy()
    pixels = result.load()
    width, height = result.size
    for x in range(width):
        for y in range(height):
            r, g, b = pixels[x, y]
            hue, saturation, value = color.rgb_to_hsv(r, g, b)
            inside = hue_min <= hue <= hue_max and saturation >= sat_min and value >= val_min
            if inside:  # потрібний колір: об'єкт
                pixels[x, y] = (255, 255, 255)
            else:  # решта: фон
                pixels[x, y] = (0, 0, 0)
    return result
