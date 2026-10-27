"""Автотести пайплайнів 1 і 2 на малих зображеннях з результатами, обчисленими вручну."""
import math
import unittest

from PIL import Image

from src import pipelines

# назви стадій пайплайнів
PIPELINE_1 = ["bilateral", "equalize", "otsu"]
PIPELINE_2 = ["wiener", "saturation", "color_segment"]
PIPELINE_2M = PIPELINE_2 + ["morphology"]  # пайплайн 2 з очищенням маски
# параметри стадій для тестів
PARAMS = {
    "bilateral": {"radius": 1, "sigma_space": 1.0, "sigma_range": 10},
    "wiener": {"radius": 1},
    "saturation": {"factor": 1.5},
    "color_segment": {"hue_min": 60, "hue_max": 170, "sat_min": 0.15, "val_min": 0.10},
    "morphology": {"radius": 1},
}


def two_level_image():
    """Зображення 4x4: ліві два стовпці яскравістю 50, праві два 200."""
    image = Image.new("RGB", (4, 4))
    for x in range(4):
        for y in range(4):
            value = 50 if x < 2 else 200
            image.putpixel((x, y), (value, value, value))
    return image


def green_red_image():
    """Зображення 4x4: ліві два стовпці зелені (0, 200, 0), праві два червоні (200, 0, 0)."""
    image = Image.new("RGB", (4, 4))
    for x in range(4):
        for y in range(4):
            image.putpixel((x, y), (0, 200, 0) if x < 2 else (200, 0, 0))
    return image


class TestPipeline1(unittest.TestCase):
    """Пайплайн 1: bilateral -> equalize -> otsu."""

    def test_chain_gives_one_output_per_stage(self):
        """Для трьох стадій отримуємо три результати того самого розміру."""
        outputs = pipelines.run_chain(two_level_image(), PIPELINE_1, PARAMS)
        self.assertEqual(len(outputs), 3)
        self.assertEqual(outputs[2].size, (4, 4))

    def test_two_level_image(self):
        """Край зберігається, далі 50 -> 0 і 200 -> 255, поріг Оцу ділить їх навпіл."""
        image = two_level_image()
        outputs = pipelines.run_chain(image, PIPELINE_1, PARAMS)
        self.assertEqual(outputs[0].tobytes(), image.tobytes())
        for index in (1, 2):
            self.assertEqual(outputs[index].getpixel((0, 0)), (0, 0, 0))
            self.assertEqual(outputs[index].getpixel((3, 3)), (255, 255, 255))

    def test_flat_image(self):
        """Однотонне зображення: стадії 1 і 2 нічого не міняють, маска чорна."""
        image = Image.new("RGB", (4, 4), (100, 100, 100))
        outputs = pipelines.run_chain(image, PIPELINE_1, PARAMS)
        self.assertEqual(outputs[1].tobytes(), image.tobytes())
        self.assertEqual(outputs[2].getpixel((2, 2)), (0, 0, 0))


class TestPipeline2(unittest.TestCase):
    """Пайплайн 2: wiener -> saturation -> color_segment."""

    def test_flat_green_image(self):
        """Однотонний зелений: стадії 1 і 2 нічого не міняють, маска вся біла."""
        image = Image.new("RGB", (4, 4), (0, 200, 0))
        outputs = pipelines.run_chain(image, PIPELINE_2, PARAMS)
        self.assertEqual(outputs[0].tobytes(), image.tobytes())
        self.assertEqual(outputs[1].tobytes(), image.tobytes())
        self.assertEqual(outputs[2].getpixel((3, 3)), (255, 255, 255))

    def test_green_red_image(self):
        """Вінер змішує колір біля межі: (33, 167, 0) і (167, 33, 0); маска: зелене біле."""
        outputs = pipelines.run_chain(green_red_image(), PIPELINE_2, PARAMS)
        row = [outputs[0].getpixel((x, 1)) for x in range(4)]
        self.assertEqual(row, [(0, 200, 0), (33, 167, 0), (167, 33, 0), (200, 0, 0)])
        mask = [outputs[2].getpixel((x, 1)) for x in range(4)]
        self.assertEqual(mask, [(255, 255, 255)] * 2 + [(0, 0, 0)] * 2)


class TestPipeline2M(unittest.TestCase):
    """Пайплайн 2 з морфологією: wiener -> saturation -> color_segment -> morphology."""

    def test_morphology_keeps_clean_block_mask(self):
        """Маска з двох суцільних половин не змінюється очищенням."""
        outputs = pipelines.run_chain(green_red_image(), PIPELINE_2M, PARAMS)
        self.assertEqual(len(outputs), 4)
        self.assertEqual(outputs[3].tobytes(), outputs[2].tobytes())


class TestEvaluate(unittest.TestCase):
    """Оцінка стадій."""

    def test_identical_outputs_give_perfect_metrics(self):
        """Однакові результати: PSNR нескінченний, SSIM = 1, IoU = 1 для маски."""
        image = two_level_image()
        outputs = pipelines.run_chain(image, PIPELINE_1, PARAMS)
        rows = pipelines.evaluate_chain(image, outputs, outputs, PIPELINE_1, 4, 1)
        self.assertTrue(math.isinf(rows[0]["psnr"]))
        self.assertAlmostEqual(rows[0]["ssim"], 1.0)
        self.assertEqual(rows[2]["iou"], 1.0)

    def test_iou_only_for_mask_stage(self):
        """IoU заповнений лише для стадії-маски; номери стадій починаються з 1."""
        image = green_red_image()
        outputs = pipelines.run_chain(image, PIPELINE_2, PARAMS)
        rows = pipelines.evaluate_chain(image, outputs, outputs, PIPELINE_2, 4, 1)
        self.assertEqual([row["iou"] for row in rows[:2]], ["", ""])
        self.assertEqual(rows[2]["iou"], 1.0)
        self.assertEqual([row["stage"] for row in rows], [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
