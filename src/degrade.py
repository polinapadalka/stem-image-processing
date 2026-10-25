"""Створення спотворених копій зображень: шум і зниження контрасту (серпанок)."""


def clamp(value):
    """Обмежує значення діапазоном 0..255 і робить його цілим."""
    # min не дає перевищити 255, max не дає опуститися нижче 0, int відкидає дробову частину
    return max(0, min(255, int(value)))


def add_gaussian_noise(image, variance, rng):
    """Адитивний гаусів шум: до кожного каналу додається число з розподілу N(0, variance)."""
    result = image.copy()  # працюємо з копією, щоб не змінювати оригінал
    pixels = result.load()  # load дає доступ до кожного пікселя за координатами pixels[x, y]
    width, height = result.size
    sigma = variance ** 0.5  # стандартне відхилення = корінь з дисперсії
    for x in range(width):  # перебираємо всі стовпці
        for y in range(height):  # і всі рядки, тобто кожен піксель
            new_color = []  # сюди збираємо нові значення R, G, B
            for c in range(3):  # c - номер каналу: 0 - червоний, 1 - зелений, 2 - синій
                # rng.gauss(0, sigma) - випадкове число із середнім 0 і розкидом sigma
                new_color.append(clamp(pixels[x, y][c] + rng.gauss(0, sigma)))
            pixels[x, y] = tuple(new_color)  # записуємо зашумлений піксель
    return result


def add_impulse_noise(image, prob, rng):
    """Імпульсний шум "сіль-перець": частка prob пікселів стає білою або чорною."""
    result = image.copy()
    pixels = result.load()
    width, height = result.size
    for x in range(width):
        for y in range(height):
            number = rng.random()  # випадкове число від 0 до 1
            if number < prob / 2:  # з імовірністю prob/2 піксель стає білим ("сіль")
                pixels[x, y] = (255, 255, 255)
            elif number > 1 - prob / 2:  # з імовірністю prob/2 піксель стає чорним ("перець")
                pixels[x, y] = (0, 0, 0)
            # в усіх інших випадках піксель не змінюється
    return result


def add_haze(image, contrast):
    """Знижує контраст за формулою NewY = K * (OldY - AveY) + AveY (імітація серпанку)."""
    result = image.copy()
    pixels = result.load()
    width, height = result.size
    averages = []  # середнє значення кожного каналу
    for c in range(3):  # перший прохід: рахуємо середнє кожного каналу
        total = 0
        for x in range(width):
            for y in range(height):
                total += pixels[x, y][c]
        averages.append(total / (width * height))
    for x in range(width):  # другий прохід: застосовуємо формулу до кожного пікселя
        for y in range(height):
            new_color = []
            for c in range(3):
                # K < 1 наближає значення до середнього, тому контраст падає
                new_color.append(clamp(contrast * (pixels[x, y][c] - averages[c]) + averages[c]))
            pixels[x, y] = tuple(new_color)
    return result


def apply_degradation(image, spec, rng):
    """Застосовує спотворення, описане в конфігурації (поле type і параметри)."""
    kind = spec["type"]  # тип спотворення з config.json
    if kind == "gaussian":
        return add_gaussian_noise(image, spec["variance"], rng)
    if kind == "impulse":
        return add_impulse_noise(image, spec["prob"], rng)
    if kind == "haze":
        return add_haze(image, spec["contrast"])
    raise ValueError("Невідомий тип спотворення: " + str(kind))  # захист від друкарських помилок