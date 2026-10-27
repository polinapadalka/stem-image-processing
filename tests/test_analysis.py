"""Автотести аналізу результатів."""
import math
import os
import tempfile
import unittest

from src import analysis, results_io


class TestStatistics(unittest.TestCase):
    """Перевірка середнього й стандартного відхилення."""

    def test_mean_and_std(self):
        """Для 1, 2, 3 середнє 2, вибіркове відхилення 1."""
        self.assertEqual(analysis.mean_std([1, 2, 3]), (2.0, 1.0))

    def test_single_value_has_zero_std(self):
        """Для одного значення відхилення 0."""
        self.assertEqual(analysis.mean_std([5]), (5.0, 0.0))

    def test_infinity_and_none_are_ignored(self):
        """Нескінченність і порожні значення не враховуються."""
        self.assertEqual(analysis.mean_std([2, math.inf, None, 4]), (3.0, math.sqrt(2)))

    def test_empty_gives_none(self):
        """Без значень середнього немає."""
        self.assertEqual(analysis.mean_std([None, None]), (None, None))


class TestSummarize(unittest.TestCase):
    """Перевірка групування."""

    def test_groups_and_means(self):
        """Два зображення з SSIM 0.8 і 0.6: середнє 0.7, відхилення 0.1414, n = 2."""
        base = {"pipeline": "p1", "degradation": "noise", "stage": 1, "stage_name": "bilateral",
                "mse": 1.0, "psnr": 30.0, "psnr_original": None, "ssim_original": None,
                "iou": None, "dice": None}
        rows = [dict(base, ssim=0.8), dict(base, ssim=0.6)]
        result = analysis.summarize(rows)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["n"], 2)
        self.assertAlmostEqual(result[0]["ssim_mean"], 0.7)
        self.assertAlmostEqual(result[0]["ssim_std"], 0.1414, places=4)
        self.assertIsNone(result[0]["iou_mean"])

    def test_different_degradations_are_separate_groups(self):
        """Різні спотворення потрапляють у різні групи."""
        base = {"pipeline": "p1", "stage": 1, "stage_name": "a", "mse": 1.0, "psnr": 1.0,
                "ssim": 1.0, "psnr_original": None, "ssim_original": None,
                "iou": None, "dice": None}
        rows = [dict(base, degradation="x"), dict(base, degradation="y")]
        self.assertEqual(len(analysis.summarize(rows)), 2)


class TestReadRows(unittest.TestCase):
    """Перевірка читання CSV."""

    def test_numbers_inf_and_empty(self):
        """Числа стають float, inf лишається inf, порожня клітинка стає None."""
        fields = ["pipeline", "degradation", "stage", "stage_name", "mse", "psnr", "ssim",
                  "psnr_original", "ssim_original", "iou", "dice"]
        row = {"pipeline": "p", "degradation": "d", "stage": 2, "stage_name": "s", "mse": 1.5,
               "psnr": math.inf, "ssim": 0.9, "psnr_original": 30.0, "ssim_original": 0.8,
               "iou": "", "dice": ""}
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "table.csv")
            results_io.write_csv(path, [row], fields)
            result = analysis.read_rows(path)[0]
        self.assertEqual(result["stage"], 2)
        self.assertTrue(math.isinf(result["psnr"]))
        self.assertIsNone(result["iou"])
        self.assertEqual(result["mse"], 1.5)


if __name__ == "__main__":
    unittest.main()