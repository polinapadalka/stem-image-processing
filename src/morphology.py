"""Морфологічна обробка чорно-білих масок: ерозія, дилатація, відкриття, закриття."""


def read_mask(image):
    """Перетворює чорно-біле зображення на таблицю True/False (True - біле, тобто об'єкт)."""
    pixels = image.load()
    width, height = image.size
    mask = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append(pixels[x, y][0] > 127)  # маска чорно-біла, тому беремо один канал
        mask.append(row)
    return mask


def write_mask(mask, image):
    """Повертає копію зображення, у якій біла й чорна частини взяті з таблиці mask."""
    result = image.copy()
    pixels = result.load()
    for y, row in enumerate(mask):
        for x, value in enumerate(row):
            pixels[x, y] = (255, 255, 255) if value else (0, 0, 0)
    return result


def erode(image, radius):
    """Ерозія: піксель лишається білим, лише якщо всі сусіди у вікні теж білі."""
    mask = read_mask(image)
    height = len(mask)
    width = len(mask[0])
    new_mask = []
    for y in range(height):
        row = []
        for x in range(width):
            keep = True
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    nx = x + dx
                    ny = y + dy
                    # на краю беремо лише наявних сусідів, тому край не з'їдається
                    if 0 <= nx < width and 0 <= ny < height and not mask[ny][nx]:
                        keep = False
            row.append(keep)
        new_mask.append(row)
    return write_mask(new_mask, image)


def dilate(image, radius):
    """Дилатація: піксель стає білим, якщо хоча б один сусід у вікні білий."""
    mask = read_mask(image)
    height = len(mask)
    width = len(mask[0])
    new_mask = []
    for y in range(height):
        row = []
        for x in range(width):
            grow = False
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    nx = x + dx
                    ny = y + dy
                    if 0 <= nx < width and 0 <= ny < height and mask[ny][nx]:
                        grow = True
            row.append(grow)
        new_mask.append(row)
    return write_mask(new_mask, image)


def opening(image, radius):
    """Відкриття: ерозія, потім дилатація. Прибирає дрібні білі плями, великі області лишає."""
    return dilate(erode(image, radius), radius)


def closing(image, radius):
    """Закриття: дилатація, потім ерозія. Заповнює дрібні чорні дірки в білих областях."""
    return erode(dilate(image, radius), radius)


def clean_mask(image, radius):
    """Очищення маски: спочатку відкриття (прибрати плями), потім закриття (заповнити дірки)."""
    return closing(opening(image, radius), radius)
