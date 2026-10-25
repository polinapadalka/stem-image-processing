"""Автотести метрик на зображеннях 3x3 з результатами, обчисленими вручну."""
import math
import unittest

from PIL import Image

from src import metrics


def flat_image(value):
    """Зображення 3x3, усі пікселі якого мають однаковий сірий колір."""
    return Image.new("RGB", (3, 3), (value, value, value))


class TestMetrics(unittest.TestCase):
    """Перевірка MSE, PSNR і SSIM."""

    def test_mse_identical_images_is_zero(self):
        """Однакові зображення: MSE = 0."""
        self.assertEqual(metrics.mse(flat_image(100), flat_image(100)), 0)

    def test_mse_one_changed_pixel(self):
        """Змінено один піксель на 10: MSE = 10^2 / 9 = 11.1111."""
        other = flat_image(100)
        other.putpixel((1, 1), (110, 110, 110))  # одну з 9 точок збільшуємо на 10
        self.assertAlmostEqual(metrics.mse(flat_image(100), other), 100 / 9, places=4)

    def test_mse_different_sizes_raises(self):
        """Різні розміри зображень: помилка ValueError."""
        with self.assertRaises(ValueError):
            metrics.mse(flat_image(100), Image.new("RGB", (4, 4)))

    def test_psnr_value(self):
        """MSE = 10: PSNR = 10 * lg(65025 / 10) = 38.13 дБ."""
        self.assertAlmostEqual(metrics.psnr(10), 38.13, places=2)

    def test_psnr_zero_mse_is_infinite(self):
        """MSE = 0: PSNR нескінченний."""
        self.assertTrue(math.isinf(metrics.psnr(0)))

    def test_ssim_identical_images_is_one(self):
        """Однакові зображення: SSIM = 1."""
        self.assertAlmostEqual(metrics.ssim(flat_image(100), flat_image(100), 3, 1), 1.0)

    def test_ssim_constant_shift(self):
        """Сталі 100 і 110: SSIM = (2*100*110 + C1) / (100^2 + 110^2 + C1) = 0.99548."""
        result = metrics.ssim(flat_image(100), flat_image(110), 3, 1)
        self.assertAlmostEqual(result, 0.99548, places=4)

    def test_compare_returns_all_metrics(self):
        """compare повертає словник із трьома метриками."""
        result = metrics.compare(flat_image(100), flat_image(100), 3, 1)
        self.assertEqual(sorted(result), ["mse", "psnr", "ssim"])


if __name__ == "__main__":
    unittest.main()