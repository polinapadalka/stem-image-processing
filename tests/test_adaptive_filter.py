"""Автотести фільтра Вінера на зображенні 3x3."""
import unittest

from PIL import Image

from src import adaptive_filter


def gray_image(values):
    """Сіре зображення 3x3 із 9 значень (рядок за рядком)."""
    image = Image.new("RGB", (3, 3))
    for index, value in enumerate(values):
        image.putpixel((index % 3, index // 3), (value, value, value))
    return image


class TestWiener(unittest.TestCase):
    """Перевірка фільтра Вінера."""

    def test_flat_image_stays_flat(self):
        """Однотонне зображення не змінюється."""
        image = gray_image([100] * 9)
        result = adaptive_filter.wiener_filter(image, 1)
        self.assertEqual(result.tobytes(), image.tobytes())

    def test_single_bright_pixel(self):
        """Яскравий піксель у центрі: результат порахований вручну."""
        image = gray_image([0, 0, 0, 0, 90, 0, 0, 0, 0])
        result = adaptive_filter.wiener_filter(image, 1)
        got = [result.getpixel((i % 3, i // 3))[0] for i in range(9)]
        self.assertEqual(got, [19, 15, 19, 15, 10, 15, 19, 15, 19])

    def test_local_statistics_of_center_window(self):
        """Середнє й дисперсія вікна 3x3 для значень 0..8."""
        image = gray_image([0, 1, 2, 3, 4, 5, 6, 7, 8])
        means, variances = adaptive_filter.local_statistics(image.load(), 3, 3, 0, 1)
        self.assertAlmostEqual(means[1][1], 4.0)
        self.assertAlmostEqual(variances[1][1], 60 / 9, places=4)


if __name__ == "__main__":
    unittest.main()
