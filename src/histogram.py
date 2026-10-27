"""Гістограмна корекція: вирівнювання гістограми яскравості (стадія 2 пайплайна 1)."""


def brightness_levels(image):
    """Повертає таблицю цілих яскравостей Y (0..255) для кожного пікселя."""
    pixels = image.load()
    width, height = image.size
    levels = []  # levels[y][x] - яскравість пікселя в рядку y і стовпці x
    for y in range(height):
        row = []
        for x in range(width):
            r, g, b = pixels[x, y]
            # формула яскравості (як у Лабі 4), округлена до цілого
            row.append(int(round(0.299 * r + 0.587 * g + 0.114 * b)))
        levels.append(row)
    return levels


def equalize_histogram(image):
    """Вирівнює гістограму яскравості, щоб використати весь діапазон 0..255.

    Нова яскравість рівня i = (cdf(i) - cdf_min) / (N - cdf_min) * 255, де cdf(i) - кількість
    пікселів із яскравістю не більшою за i, cdf_min - перше ненульове cdf, N - число пікселів.
    Колір зберігається: канали пікселя множаться на один коефіцієнт нова/стара яскравість.
    """
    width, height = image.size
    levels = brightness_levels(image)

    counts = [0] * 256  # гістограма: скільки пікселів має кожну яскравість
    for row in levels:
        for level in row:
            counts[level] += 1

    cdf = [0] * 256  # накопичена гістограма: скільки пікселів мають яскравість не більшу за i
    total = 0
    for i in range(256):
        total += counts[i]
        cdf[i] = total

    cdf_min = 0  # перше ненульове значення накопиченої гістограми
    for i in range(256):
        if cdf[i] > 0:
            cdf_min = cdf[i]
            break

    result = image.copy()  # результат пишемо в копію
    pixel_count = width * height
    # якщо всі пікселі мають однакову яскравість, вирівнювати нічого (і ділити на 0 не можна)
    if pixel_count == cdf_min:
        return result

    mapping = []  # mapping[i] - нова яскравість для старої яскравості i
    for i in range(256):
        value = (cdf[i] - cdf_min) / (pixel_count - cdf_min) * 255
        mapping.append(max(0, int(round(value))))

    pixels = result.load()
    for y in range(height):
        for x in range(width):
            old = levels[y][x]  # стара яскравість пікселя
            new = mapping[old]  # нова яскравість
            if old == 0:  # на чорне ділити не можна: ставимо сірий колір потрібної яскравості
                pixels[x, y] = (new, new, new)
            else:
                ratio = new / old  # у скільки разів змінюється яскравість
                r, g, b = pixels[x, y]
                # усі канали множимо на один коефіцієнт, щоб відтінок не змінювався
                pixels[x, y] = (min(255, int(round(r * ratio))),
                                min(255, int(round(g * ratio))),
                                min(255, int(round(b * ratio))))
    return result
