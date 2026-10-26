"""Автотести вирівнювання гістограми на малих зображеннях з результатами, обчисленими вручну."""
import unittest

from PIL import Image

from src import histogram


def gray_image(values):
    """Сіре зображення 3x3 із 9 значень (рядок за рядком)."""
    image = Image.new("RGB", (3, 3))
    for index, value in enumerate(values):
        image.putpixel((index % 3, index // 3), (value, value, value))
    return image


class TestEqualize(unittest.TestCase):
    """Перевірка вирівнювання гістограми."""

    def test_known_values(self):
        """Яскравості 10 (2 шт.), 20 (3 шт.), 30 (4 шт.): cdf = 2, 5, 9; cdf_min = 2.

        Нові значення: 10 -> 0; 20 -> (5-2)/(9-2)*255 = 109.3 -> 109; 30 -> 255.
        """
        image = gray_image([10, 10, 20, 20, 20, 30, 30, 30, 30])
        result = histogram.equalize_histogram(image)
        got = [result.getpixel((i % 3, i // 3))[0] for i in range(9)]
        self.assertEqual(got, [0, 0, 109, 109, 109, 255, 255, 255, 255])

    def test_low_contrast_is_stretched(self):
        """Два близькі рівні 100 і 110 розтягуються до 0 і 255."""
        image = gray_image([100, 100, 100, 100, 110, 110, 110, 110, 110])
        result = histogram.equalize_histogram(image)
        self.assertEqual(result.getpixel((0, 0)), (0, 0, 0))
        self.assertEqual(result.getpixel((2, 2)), (255, 255, 255))

    def test_flat_image_unchanged(self):
        """Однотонне зображення не змінюється (ділення на нуль не виникає)."""
        image = gray_image([120] * 9)
        result = histogram.equalize_histogram(image)
        self.assertEqual(result.tobytes(), image.tobytes())

    def test_color_scaled_by_one_ratio(self):
        """Піксель (200,100,100) має Y = 130; найтемніший (100,50,50) має Y = 65.

        Після вирівнювання 65 -> 0, 130 -> 255; канали світлого множаться на 255/130 = 1.96:
        200 -> 255 (обмеження зверху), 100 -> 196.
        """
        image = Image.new("RGB", (2, 1))
        image.putpixel((0, 0), (100, 50, 50))
        image.putpixel((1, 0), (200, 100, 100))
        result = histogram.equalize_histogram(image)
        self.assertEqual(result.getpixel((0, 0)), (0, 0, 0))
        self.assertEqual(result.getpixel((1, 0)), (255, 196, 196))


if __name__ == "__main__":
    unittest.main()