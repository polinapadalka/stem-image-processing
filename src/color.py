"""Колірні перетворення: RGB <-> HSV і підвищення насиченості (стадія 2 пайплайна 2)."""


def rgb_to_hsv(r, g, b):
    """Перетворює колір RGB (0..255) на HSV: відтінок 0..360, насиченість і яскравість 0..1."""
    r = r / 255  # переводимо канали в діапазон 0..1
    g = g / 255
    b = b / 255
    biggest = max(r, g, b)
    smallest = min(r, g, b)
    delta = biggest - smallest  # різниця між найбільшим і найменшим каналом
    value = biggest  # яскравість V - найбільший канал
    if biggest == 0:  # чорний колір: насиченість 0
        saturation = 0
    else:
        saturation = delta / biggest
    if delta == 0:  # сірий колір: відтінку немає
        hue = 0
    elif biggest == r:  # переважає червоний
        hue = 60 * (((g - b) / delta) % 6)
    elif biggest == g:  # переважає зелений
        hue = 60 * ((b - r) / delta + 2)
    else:  # переважає синій
        hue = 60 * ((r - g) / delta + 4)
    return hue, saturation, value


def hsv_to_rgb(hue, saturation, value):
    """Перетворює колір HSV назад у RGB (0..255)."""
    hue = hue % 360  # відтінок по колу: 360 - це те саме, що 0
    chroma = value * saturation  # "чистота" кольору
    x = chroma * (1 - abs((hue / 60) % 2 - 1))
    shift = value - chroma  # додається до всіх каналів
    sector = int(hue // 60)  # у якому з шести секторів кола лежить відтінок
    if sector == 0:
        r, g, b = chroma, x, 0
    elif sector == 1:
        r, g, b = x, chroma, 0
    elif sector == 2:
        r, g, b = 0, chroma, x
    elif sector == 3:
        r, g, b = 0, x, chroma
    elif sector == 4:
        r, g, b = x, 0, chroma
    else:
        r, g, b = chroma, 0, x
    return (int(round((r + shift) * 255)),
            int(round((g + shift) * 255)),
            int(round((b + shift) * 255)))


def saturation_boost(image, factor):
    """Множить насиченість пікселів на factor (максимум 1); відтінок і яскравість не змінюються."""
    result = image.copy()
    pixels = result.load()
    width, height = result.size
    for x in range(width):
        for y in range(height):
            r, g, b = pixels[x, y]
            hue, saturation, value = rgb_to_hsv(r, g, b)
            saturation = min(1, saturation * factor)  # насиченість не може перевищити 1
            pixels[x, y] = hsv_to_rgb(hue, saturation, value)
    return result