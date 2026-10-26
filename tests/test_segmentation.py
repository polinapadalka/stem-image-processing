"""Автотести сегментації на малих зображеннях з результатами, обчисленими вручну."""
import unittest

from PIL import Image

from src import segmentation

# параметри для виділення зелені: відтінок 60..170, насиченість від 0.15, яскравість від 0.10
GREEN = (60, 170, 0.15, 0.10)


def gray_image(values):
    """Сіре зображення 3x3 із 9 значень (рядок за рядком)."""
    image = Image.new("RGB", (3, 3))
    for index, value in enumerate(values):
        image.putpixel((index % 3, index // 3), (value, value, value))
    return image


class TestOtsu(unittest.TestCase):
    """Перевірка порога Оцу й сегментації за яскравістю."""

    def test_two_levels_threshold(self):
        """Чотири пікселі 50 і п'ять 200: поріг 50 (найменший із рівноцінних)."""
        image = gray_image([50, 50, 50, 50, 200, 200, 200, 200, 200])
        self.assertEqual(segmentation.otsu_threshold(image), 50)

    def test_segmentation_makes_black_and_white(self):
        """Темні пікселі стають чорними, світлі білими."""
        image = gray_image([50, 50, 50, 50, 200, 200, 200, 200, 200])
        result = segmentation.otsu_segmentation(image)
        self.assertEqual(result.getpixel((0, 0)), (0, 0, 0))
        self.assertEqual(result.getpixel((2, 2)), (255, 255, 255))

    def test_three_groups_picks_best_split(self):
        """Значення 10, 100, 200: поріг 100 дає більшу міжкласову дисперсію, ніж 10."""
        image = gray_image([10, 10, 10, 100, 100, 200, 200, 200, 200])
        self.assertEqual(segmentation.otsu_threshold(image), 100)

    def test_flat_image_is_all_background(self):
        """Однотонне зображення не можна поділити: усе стає чорним."""
        image = gray_image([120] * 9)
        result = segmentation.otsu_segmentation(image)
        self.assertEqual(result.getpixel((1, 1)), (0, 0, 0))


class TestColorSegmentation(unittest.TestCase):
    """Перевірка колірної сегментації."""

    def segment(self, color):
        """Сегментує зображення з одного пікселя й повертає колір маски."""
        image = Image.new("RGB", (1, 1), color)
        return segmentation.color_segmentation(image, *GREEN).getpixel((0, 0))

    def test_green_is_object(self):
        """Зелений (0, 200, 0): відтінок 120 у межах, насиченість 1, яскравість 0.78."""
        self.assertEqual(self.segment((0, 200, 0)), (255, 255, 255))

    def test_yellow_green_is_object(self):
        """Жовто-зелений (150, 200, 0): відтінок 75 у межах 60..170."""
        self.assertEqual(self.segment((150, 200, 0)), (255, 255, 255))

    def test_red_is_background(self):
        """Червоний (200, 0, 0): відтінок 0 поза межами."""
        self.assertEqual(self.segment((200, 0, 0)), (0, 0, 0))

    def test_dark_green_is_background(self):
        """Дуже темний зелений (0, 20, 0): яскравість 0.078 менша за 0.10."""
        self.assertEqual(self.segment((0, 20, 0)), (0, 0, 0))

    def test_grayish_green_is_background(self):
        """Сіро-зелений (120, 130, 120): насиченість 0.077 менша за 0.15."""
        self.assertEqual(self.segment((120, 130, 120)), (0, 0, 0))


if __name__ == "__main__":
    unittest.main()