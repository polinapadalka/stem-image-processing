"""Автотести пайплайна: стадії bilateral, equalize, otsu на малих зображеннях."""
import math
import unittest

from PIL import Image

from src import pipelines

# назви стадій пайплайна 1 і параметри білатерального фільтра для тестів
PIPELINE_1 = ["bilateral", "equalize", "otsu"]
PARAMS = {"bilateral": {"radius": 1, "sigma_space": 1.0, "sigma_range": 10}}


def two_level_image():
    """Зображення 4x4: ліві два стовпці мають яскравість 50, праві два - 200."""
    image = Image.new("RGB", (4, 4))
    for x in range(4):
        for y in range(4):
            value = 50 if x < 2 else 200
            image.putpixel((x, y), (value, value, value))
    return image


class TestPipeline(unittest.TestCase):
    """Перевірка запуску пайплайна й оцінки його стадій."""

    def test_chain_gives_one_output_per_stage(self):
        """Для трьох стадій отримуємо три результати того самого розміру."""
        outputs = pipelines.run_chain(two_level_image(), PIPELINE_1, PARAMS)
        self.assertEqual(len(outputs), 3)
        self.assertEqual(outputs[2].size, (4, 4))

    def test_two_level_image_through_pipeline_1(self):
        """Ручний розрахунок для зображення з двома рівнями 50 і 200.
        Стадія 1: сусіди з іншого боку краю мають вагу майже 0, тож зображення не змінюється.
        Стадія 2: cdf(50) = 8, cdf(200) = 16, cdf_min = 8: 50 -> 0, 200 -> 255.
        Стадія 3: поріг Оцу = 0, тому світле (255) стає білим, а темне (0) чорним.
        """
        image = two_level_image()
        outputs = pipelines.run_chain(image, PIPELINE_1, PARAMS)
        self.assertEqual(outputs[0].tobytes(), image.tobytes())
        for index in (1, 2):
            self.assertEqual(outputs[index].getpixel((0, 0)), (0, 0, 0))
            self.assertEqual(outputs[index].getpixel((3, 3)), (255, 255, 255))

    def test_flat_image_through_pipeline_1(self):
        """Однотонне зображення: стадії 1 і 2 його не змінюють, а маска повністю чорна."""
        image = Image.new("RGB", (4, 4), (100, 100, 100))
        outputs = pipelines.run_chain(image, PIPELINE_1, PARAMS)
        self.assertEqual(outputs[1].tobytes(), image.tobytes())
        self.assertEqual(outputs[2].getpixel((2, 2)), (0, 0, 0))

    def test_identical_outputs_give_perfect_metrics(self):
        """Однакові результати: PSNR нескінченний, SSIM = 1, IoU = 1 для маски."""
        image = two_level_image()
        outputs = pipelines.run_chain(image, PIPELINE_1, PARAMS)
        rows = pipelines.evaluate_chain(image, outputs, outputs, PIPELINE_1, 4, 1)
        self.assertTrue(math.isinf(rows[0]["psnr"]))
        self.assertAlmostEqual(rows[0]["ssim"], 1.0)
        self.assertEqual(rows[2]["iou"], 1.0)

    def test_iou_only_for_mask_stage(self):
        """IoU й Дайс заповнені лише для стадії-маски; номери стадій починаються з 1."""
        image = two_level_image()
        outputs = pipelines.run_chain(image, PIPELINE_1, PARAMS)
        rows = pipelines.evaluate_chain(image, outputs, outputs, PIPELINE_1, 4, 1)
        self.assertEqual(rows[0]["iou"], "")
        self.assertEqual(rows[1]["iou"], "")
        self.assertEqual([row["stage"] for row in rows], [1, 2, 3])
        self.assertEqual(rows[2]["stage_name"], "otsu")


if __name__ == "__main__":
    unittest.main()