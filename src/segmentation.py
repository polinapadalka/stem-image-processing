"""Сегментація: поділ зображення на об'єкт і фон за порогом Оцу (стадія 3 пайплайна 1)."""
from src import histogram


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