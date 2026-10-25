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


if __name__ == "__main__":
    unittest.main()