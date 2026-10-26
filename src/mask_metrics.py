"""Метрики для чорно-білих масок сегментації: IoU і коефіцієнт Дайса."""


def count_overlap(mask_a, mask_b):
    """Рахує пікселі об'єкта (білі, яскравість > 127): у першій масці, у другій і в обох."""
    if mask_a.size != mask_b.size:
        raise ValueError("Маски мають різні розміри")
    pixels_a = mask_a.load()
    pixels_b = mask_b.load()
    width, height = mask_a.size
    count_a = 0  # скільки білих пікселів у першій масці
    count_b = 0  # скільки білих пікселів у другій масці
    both = 0  # скільки пікселів білі в обох масках одночасно
    for x in range(width):
        for y in range(height):
            white_a = pixels_a[x, y][0] > 127  # маска чорно-біла, тому беремо один канал
            white_b = pixels_b[x, y][0] > 127
            if white_a:
                count_a += 1
            if white_b:
                count_b += 1
            if white_a and white_b:
                both += 1
    return count_a, count_b, both


def iou(mask_a, mask_b):
    """IoU = перетин / об'єднання білих областей двох масок (від 0 до 1)."""
    count_a, count_b, both = count_overlap(mask_a, mask_b)
    union = count_a + count_b - both  # об'єднання: усе, що біле хоча б в одній масці
    if union == 0:  # обидві маски порожні, тобто однакові
        return 1.0
    return both / union


def dice(mask_a, mask_b):
    """Коефіцієнт Дайса = 2 * перетин / (сума білих пікселів двох масок)."""
    count_a, count_b, both = count_overlap(mask_a, mask_b)
    total = count_a + count_b
    if total == 0:  # обидві маски порожні, тобто однакові
        return 1.0
    return 2 * both / total