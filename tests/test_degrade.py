"""Автотести спотворень: шуму й зниження контрасту."""
import random  # random.Random(seed) - генератор із фіксованим початковим числом
import unittest

from PIL import Image

from src import degrade


class TestDegrade(unittest.TestCase):
    """Перевірка шуму та зниження контрасту."""

    def test_clamp_limits_values(self):
        """clamp не пропускає значення за межі 0..255 і відкидає дробову частину."""
        self.assertEqual(degrade.clamp(300), 255)
        self.assertEqual(degrade.clamp(-5), 0)
        self.assertEqual(degrade.clamp(12.7), 12)

    def test_same_seed_gives_same_noise(self):
        """З однаковим seed шум однаковий."""
        image = Image.new("RGB", (5, 5), (100, 100, 100))
        first = degrade.add_gaussian_noise(image, 100, random.Random("abc"))
        second = degrade.add_gaussian_noise(image, 100, random.Random("abc"))
        self.assertEqual(first.tobytes(), second.tobytes())

    def test_zero_variance_keeps_image(self):
        """Дисперсія 0: випадкове число завжди 0, зображення не змінюється."""
        image = Image.new("RGB", (4, 4), (80, 90, 100))
        result = degrade.add_gaussian_noise(image, 0, random.Random("x"))
        self.assertEqual(result.tobytes(), image.tobytes())

    def test_haze_formula(self):
        """Значення 0, 100, 200 (середнє 100) при K = 0.5 дають 50, 100, 150."""
        image = Image.new("RGB", (3, 1))
        for x, value in enumerate((0, 100, 200)):
            image.putpixel((x, 0), (value, value, value))
        result = degrade.add_haze(image, 0.5)
        self.assertEqual([result.getpixel((x, 0))[0] for x in range(3)], [50, 100, 150])

    def test_impulse_zero_probability_keeps_image(self):
        """Імовірність 0: зображення не змінюється."""
        image = Image.new("RGB", (4, 4), (120, 120, 120))
        result = degrade.add_impulse_noise(image, 0, random.Random("x"))
        self.assertEqual(result.tobytes(), image.tobytes())

    def test_impulse_full_probability_makes_black_or_white(self):
        """Імовірність 1: кожен піксель стає чорним або білим."""
        image = Image.new("RGB", (6, 6), (120, 120, 120))
        result = degrade.add_impulse_noise(image, 1, random.Random("x"))
        for x in range(6):
            for y in range(6):
                self.assertIn(result.getpixel((x, y)), [(0, 0, 0), (255, 255, 255)])

    def test_unknown_degradation_raises(self):
        """Невідомий тип спотворення: ValueError."""
        image = Image.new("RGB", (2, 2))
        with self.assertRaises(ValueError):
            degrade.apply_degradation(image, {"type": "unknown"}, random.Random("x"))


if __name__ == "__main__":
    unittest.main()
