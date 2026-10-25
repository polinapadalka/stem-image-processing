"""Автотести білатерального фільтра на зображеннях 3x3 з результатами, обчисленими вручну."""
import unittest

from PIL import Image

from src import filtering


def gray_image(values):
    """Сіре зображення 3x3 із 9 значень (рядок за рядком)."""
    image = Image.new("RGB", (3, 3))
    for index, value in enumerate(values):
        # index % 3 - стовпець, index // 3 - рядок
        image.putpixel((index % 3, index // 3), (value, value, value))
    return image


class TestBilateral(unittest.TestCase):
    """Перевірка білатерального фільтра."""

    def test_flat_image_stays_flat(self):
        """Однотонне зображення не змінюється: усі сусіди мають однаковий колір."""
        image = gray_image([100] * 9)
        result = filtering.bilateral_filter(image, 1, 1.0, 30)
        self.assertEqual(result.tobytes(), image.tobytes())

    def test_outlier_is_ignored(self):
        """Викид 255 серед значень 100 має вагу майже 0, тож центр лишається 100."""
        values = [100] * 9
        values[0] = 255  # "сіль" у куті; центр (індекс 4) має значення 100
        result = filtering.bilateral_filter(gray_image(values), 1, 1.0, 10)
        self.assertEqual(result.getpixel((1, 1)), (100, 100, 100))

    def test_wide_sigmas_give_plain_mean(self):
        """При дуже великих sigma всі ваги дорівнюють 1: центр = середнє = (0+10+...+80)/9 = 40."""
        values = [0, 10, 20, 30, 40, 50, 60, 70, 80]
        result = filtering.bilateral_filter(gray_image(values), 1, 1e6, 1e6)
        self.assertEqual(result.getpixel((1, 1)), (40, 40, 40))

    def test_corner_uses_only_existing_neighbors(self):
        """Кут з великими sigma: середнє чотирьох наявних значень (0, 10, 30, 40) = 20."""
        values = [0, 10, 20, 30, 40, 50, 60, 70, 80]
        result = filtering.bilateral_filter(gray_image(values), 1, 1e6, 1e6)
        self.assertEqual(result.getpixel((0, 0)), (20, 20, 20))

    def test_edge_is_preserved(self):
        """Різкий край 0 | 200 зберігається: сусіди з іншого боку краю майже не впливають."""
        values = [0, 0, 200, 0, 0, 200, 0, 0, 200]
        result = filtering.bilateral_filter(gray_image(values), 1, 1.0, 10)
        self.assertEqual(result.getpixel((1, 1)), (0, 0, 0))  # лівий бік краю лишається 0
        self.assertEqual(result.getpixel((2, 1)), (200, 200, 200))  # правий бік лишається 200


if __name__ == "__main__":
    unittest.main()