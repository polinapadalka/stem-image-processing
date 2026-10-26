"""Автотести порога Оцу на малих зображеннях з результатами, обчисленими вручну."""
import unittest

from PIL import Image

from src import segmentation


def gray_image(values):
    """Сіре зображення 3x3 із 9 значень (рядок за рядком)."""
    image = Image.new("RGB", (3, 3))
    for index, value in enumerate(values):
        image.putpixel((index % 3, index // 3), (value, value, value))
    return image


class TestOtsu(unittest.TestCase):
    """Перевірка порога Оцу й сегментації."""

    def test_two_levels_threshold(self):
        """Чотири пікселі 50 і п'ять 200: найкращий поділ між ними.
        Для будь-якого порога від 50 до 199 міжкласова дисперсія однакова: 4 * 5 * 150^2.
        Обирається найменший із них, тобто 50.
        """
        image = gray_image([50, 50, 50, 50, 200, 200, 200, 200, 200])
        self.assertEqual(segmentation.otsu_threshold(image), 50)

    def test_segmentation_makes_black_and_white(self):
        """Темні пікселі стають чорними, світлі білими."""
        image = gray_image([50, 50, 50, 50, 200, 200, 200, 200, 200])
        result = segmentation.otsu_segmentation(image)
        self.assertEqual(result.getpixel((0, 0)), (0, 0, 0))  # перший піксель: 50
        self.assertEqual(result.getpixel((2, 2)), (255, 255, 255))  # останній піксель: 200

    def test_three_groups_picks_best_split(self):
        """Значення 10, 10, 10, 100, 100, 200, 200, 200, 200: порівнюємо пороги 10 і 100.
        Поріг 10: w0 = 3, m0 = 10, w1 = 6, m1 = 1000 / 6 = 166.67: 3 * 6 * 156.67^2 = 441800.
        Поріг 100: w0 = 5, m0 = 230 / 5 = 46, w1 = 4, m1 = 200: 5 * 4 * 154^2 = 474320.
        Друге число більше, тому поріг Оцу дорівнює 100.
        """
        image = gray_image([10, 10, 10, 100, 100, 200, 200, 200, 200])
        self.assertEqual(segmentation.otsu_threshold(image), 100)

    def test_flat_image_is_all_background(self):
        """Однотонне зображення не можна поділити: усе стає чорним (фоном)."""
        image = gray_image([120] * 9)
        result = segmentation.otsu_segmentation(image)
        self.assertEqual(result.getpixel((1, 1)), (0, 0, 0))


if __name__ == "__main__":
    unittest.main()