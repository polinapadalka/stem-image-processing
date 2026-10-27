"""Метрики якості зображень: MSE, PSNR, SSIM. Усе обчислено вручну."""
# math потрібен для логарифма й нескінченності
import math

# максимальне значення каналу для 8-бітного зображення
MAX_VALUE = 255


def mse(image_a, image_b):
    """Середній квадрат різниці по всіх пікселях і каналах (MSE)."""
    # порівнювати можна лише зображення однакового розміру
    if image_a.size != image_b.size:
        raise ValueError("Зображення мають різні розміри")
    pixels_a = image_a.load()  # доступ до пікселів першого зображення
    pixels_b = image_b.load()  # доступ до пікселів другого зображення
    width, height = image_a.size
    error = 0  # сума квадратів різниць
    for x in range(width):
        for y in range(height):
            for c in range(3):  # по трьох каналах R, G, B
                diff = pixels_a[x, y][c] - pixels_b[x, y][c]  # різниця значень каналу
                error += diff * diff  # квадрат прибирає знак різниці
    return error / (width * height * 3)  # середнє: сума поділена на кількість значень


def psnr(mse_value):
    """Піковий сигнал/шум у дБ: 10 * lg(255^2 / MSE)."""
    # для однакових зображень MSE = 0 і ділити не можна: PSNR вважаємо нескінченним
    if mse_value == 0:
        return math.inf
    return 10 * math.log10(MAX_VALUE * MAX_VALUE / mse_value)


def to_gray(image):
    """Перетворює зображення на таблицю яскравостей Y = 0.299R + 0.587G + 0.114B."""
    pixels = image.load()
    width, height = image.size
    gray = []  # таблиця: gray[y][x] - яскравість пікселя в рядку y і стовпці x
    for y in range(height):
        row = []
        for x in range(width):
            r, g, b = pixels[x, y]
            row.append(0.299 * r + 0.587 * g + 0.114 * b)  # формула яскравості з Лаби 4
        gray.append(row)
    return gray


def ssim(image_a, image_b, window=8, step=4):
    """Індекс структурної подібності (SSIM), усереднений по вікнах window x window.

    Формула для одного вікна:
    ((2*mx*my + C1) * (2*cov + C2)) / ((mx^2 + my^2 + C1) * (vx + vy + C2)).
    """
    if image_a.size != image_b.size:
        raise ValueError("Зображення мають різні розміри")
    width, height = image_a.size
    window = min(window, width, height)  # для дуже малих зображень беремо все зображення
    gray_a = to_gray(image_a)  # SSIM рахуємо за яскравістю
    gray_b = to_gray(image_b)
    c1 = (0.01 * MAX_VALUE) ** 2  # константи, щоб не ділити на нуль на однотонних ділянках
    c2 = (0.03 * MAX_VALUE) ** 2
    count = window * window  # кількість пікселів у вікні
    total = 0  # сума SSIM усіх вікон
    windows = 0  # кількість вікон
    for top in range(0, height - window + 1, step):  # верхня межа вікна
        for left in range(0, width - window + 1, step):  # ліва межа вікна
            # суми для середніх, дисперсій і коваріації
            sum_a = sum_b = sum_aa = sum_bb = sum_ab = 0
            for y in range(top, top + window):
                for x in range(left, left + window):
                    value_a = gray_a[y][x]
                    value_b = gray_b[y][x]
                    sum_a += value_a
                    sum_b += value_b
                    sum_aa += value_a * value_a
                    sum_bb += value_b * value_b
                    sum_ab += value_a * value_b
            mean_a = sum_a / count  # середня яскравість у вікні першого зображення
            mean_b = sum_b / count  # і другого
            var_a = sum_aa / count - mean_a * mean_a  # дисперсія першого
            var_b = sum_bb / count - mean_b * mean_b  # дисперсія другого
            cov = sum_ab / count - mean_a * mean_b  # коваріація: наскільки вони змінюються разом
            numerator = (2 * mean_a * mean_b + c1) * (2 * cov + c2)
            denominator = (mean_a ** 2 + mean_b ** 2 + c1) * (var_a + var_b + c2)
            total += numerator / denominator  # SSIM цього вікна
            windows += 1
    return total / windows  # середнє по всіх вікнах


def compare(image_a, image_b, window=8, step=4):
    """Повертає словник усіх метрик для пари зображень."""
    mse_value = mse(image_a, image_b)
    return {
        "mse": mse_value,
        "psnr": psnr(mse_value),
        "ssim": ssim(image_a, image_b, window, step),
    }
