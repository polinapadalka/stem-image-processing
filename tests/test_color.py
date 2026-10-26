"""Автотести колірних перетворень."""
import unittest

from PIL import Image

from src import color


class TestColor(unittest.TestCase):
    """Перевірка RGB <-> HSV і підвищення насиченості."""

    def test_primary_colors_to_hsv(self):
        """Червоний, зелений і синій мають відтінки 0, 120 і 240."""
        self.assertEqual(color.rgb_to_hsv(255, 0, 0), (0, 1, 1))
        self.assertEqual(color.rgb_to_hsv(0, 255, 0), (120, 1, 1))
        self.assertEqual(color.rgb_to_hsv(0, 0, 255), (240, 1, 1))

    def test_gray_has_no_saturation(self):
        """Сірий колір: насиченість 0, відтінок 0, яскравість 0.5."""
        hue, saturation, value = color.rgb_to_hsv(128, 128, 128)
        self.assertEqual((hue, saturation), (0, 0))
        self.assertAlmostEqual(value, 128 / 255)

    def test_round_trip(self):
        """RGB -> HSV -> RGB повертає той самий колір."""
        for rgb in [(200, 100, 100), (10, 200, 30), (0, 0, 0), (255, 255, 255), (17, 34, 200)]:
            self.assertEqual(color.hsv_to_rgb(*color.rgb_to_hsv(*rgb)), rgb)

    def test_saturation_boost_value(self):
        """Колір (200, 100, 100) при factor 1.5 стає (200, 50, 50)."""
        image = Image.new("RGB", (1, 1), (200, 100, 100))
        result = color.saturation_boost(image, 1.5)
        self.assertEqual(result.getpixel((0, 0)), (200, 50, 50))

    def test_gray_pixel_unchanged_by_boost(self):
        """Сірий піксель не має насиченості, тож не змінюється."""
        image = Image.new("RGB", (1, 1), (120, 120, 120))
        result = color.saturation_boost(image, 2)
        self.assertEqual(result.getpixel((0, 0)), (120, 120, 120))


if __name__ == "__main__":
    unittest.main()