"""Адаптивний фільтр Вінера (стадія 1 пайплайна 2)."""


def local_statistics(pixels, width, height, channel, radius):
    """Для кожного пікселя рахує середнє й дисперсію значень каналу у вікні навколо нього."""
    means = []  # means[y][x] - середнє у вікні навколо пікселя (x, y)
    variances = []  # variances[y][x] - дисперсія у вікні
    for y in range(height):
        mean_row = []
        variance_row = []
        for x in range(width):
            total = 0  # сума значень вікна
            total_sq = 0  # сума квадратів значень вікна
            count = 0  # скільки пікселів у вікні
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    nx = x + dx
                    ny = y + dy
                    if 0 <= nx < width and 0 <= ny < height:  # на краю беремо лише наявних сусідів
                        value = pixels[nx, ny][channel]
                        total += value
                        total_sq += value * value
                        count += 1
            mean = total / count
            mean_row.append(mean)
            # дисперсія = середнє квадратів - квадрат середнього
            variance_row.append(total_sq / count - mean * mean)
        means.append(mean_row)
        variances.append(variance_row)
    return means, variances


def wiener_filter(image, radius):
    
    pixels = image.load()
    width, height = image.size
    result = image.copy()
    new_pixels = result.load()
    for channel in range(3):  # кожен канал обробляємо окремо
        means, variances = local_statistics(pixels, width, height, channel, radius)
        # оцінка дисперсії шуму: середнє всіх локальних дисперсій
        noise = 0
        for row in variances:
            noise += sum(row)
        noise = noise / (width * height)
        for y in range(height):
            for x in range(width):
                mean = means[y][x]
                variance = variances[y][x]
                value = pixels[x, y][channel]
                if variance > noise:  # у вікні більше змін, ніж від шуму: це деталі, зберігаємо їх
                    value = mean + (variance - noise) / variance * (value - mean)
                else:  # вікно виглядає як шум: замінюємо на середнє
                    value = mean
                colors = list(new_pixels[x, y])  # поточний колір результату
                colors[channel] = max(0, min(255, int(round(value))))
                new_pixels[x, y] = tuple(colors)
    return result