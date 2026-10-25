"""Фільтри шумозаглушення: білатеральний фільтр (стадія 1 пайплайна 1)."""
# math потрібен для експоненти exp
import math


def bilateral_filter(image, radius, sigma_space, sigma_range):
    """Білатеральний фільтр: усереднює сусідів з вагою за відстанню і за схожістю кольору.

    Вага сусіда = exp(-d^2 / (2 * sigma_space^2)) * exp(-c^2 / (2 * sigma_range^2)),
    де d - відстань до центрального пікселя, c - відстань між кольорами (R, G, B).
    """
    pixels = image.load()  # звідси читаємо старі значення
    width, height = image.size
    result = image.copy()  # результат пишемо в копію, щоб нові значення не впливали на сусідів
    new_pixels = result.load()

    # ваги за відстанню однакові для всіх пікселів, тому рахуємо їх один раз
    space_weights = {}  # ключ - зсув (dx, dy), значення - вага цього зсуву
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            space_weights[(dx, dy)] = math.exp(-(dx * dx + dy * dy) / (2 * sigma_space ** 2))

    range_denominator = 2 * sigma_range ** 2  # знаменник для ваги за схожістю кольору

    for x in range(width):  # перебираємо кожен піксель зображення
        for y in range(height):
            center = pixels[x, y]  # колір центрального пікселя (R, G, B)
            sums = [0.0, 0.0, 0.0]  # зважені суми кольорів сусідів по каналах
            weight_sum = 0.0  # сума всіх ваг, щоб потім поділити
            for dx in range(-radius, radius + 1):  # перебираємо сусідів у вікні
                for dy in range(-radius, radius + 1):
                    nx = x + dx  # координати сусіда
                    ny = y + dy
                    if 0 <= nx < width and 0 <= ny < height:  # на краю беремо лише наявних сусідів
                        neighbor = pixels[nx, ny]
                        diff_r = neighbor[0] - center[0]  # різниця кольорів за каналами
                        diff_g = neighbor[1] - center[1]
                        diff_b = neighbor[2] - center[2]
                        color_dist = diff_r * diff_r + diff_g * diff_g + diff_b * diff_b
                        # вага = вага за відстанню * вага за схожістю кольору
                        weight = space_weights[(dx, dy)] * math.exp(-color_dist / range_denominator)
                        weight_sum += weight
                        for c in range(3):
                            sums[c] += weight * neighbor[c]  # додаємо колір сусіда з його вагою
            # weight_sum не буває нулем: центральний піксель сам для себе має вагу 1
            new_color = []
            for c in range(3):
                new_color.append(int(round(sums[c] / weight_sum)))  # зважене середнє
            new_pixels[x, y] = tuple(new_color)
    return result