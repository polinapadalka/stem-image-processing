"""Автотести запуску стадій за назвою."""
import unittest

from PIL import Image

from src import stages

# параметри білатерального фільтра для тесту
BILATERAL_PARAMS = {"radius": 1, "sigma_space": 1.0, "sigma_range": 30}


class TestStages(unittest.TestCase):
    """Перевірка вибору стадії за назвою."""

    def test_unknown_stage_raises(self):
        """Невідома назва стадії: ValueError."""
        with self.assertRaises(ValueError):
            stages.run_stage("nonsense", Image.new("RGB", (3, 3)), {})

    def test_bilateral_stage_keeps_size_and_flat_image(self):
        """Стадія bilateral зберігає розмір, а однотонне зображення лишається однотонним."""
        image = Image.new("RGB", (4, 4), (90, 90, 90))
        result = stages.run_stage("bilateral", image, BILATERAL_PARAMS)
        self.assertEqual(result.size, (4, 4))
        self.assertEqual(result.tobytes(), image.tobytes())

    def test_equalize_stage_keeps_size(self):
        """Стадія equalize повертає зображення того самого розміру."""
        image = Image.new("RGB", (3, 3), (50, 60, 70))
        self.assertEqual(stages.run_stage("equalize", image, {}).size, (3, 3))

    def test_otsu_stage_gives_black_and_white(self):
        """Стадія otsu повертає лише чорні й білі пікселі."""
        image = Image.new("RGB", (2, 1))
        image.putpixel((0, 0), (30, 30, 30))
        image.putpixel((1, 0), (220, 220, 220))
        result = stages.run_stage("otsu", image, {})
        self.assertEqual([result.getpixel((0, 0)), result.getpixel((1, 0))],
                         [(0, 0, 0), (255, 255, 255)])

    def test_wiener_stage_keeps_flat_image(self):
        """Стадія wiener не змінює однотонне зображення."""
        image = Image.new("RGB", (4, 4), (70, 80, 90))
        result = stages.run_stage("wiener", image, {"radius": 1})
        self.assertEqual(result.tobytes(), image.tobytes())


if __name__ == "__main__":
    unittest.main()