"""Автотести підготовки даних для графіків і створення файлів."""
import os
import tempfile
import unittest

from src import analysis, plots


def row(pipeline, degradation, stage, iou, image="a00"):
    """Рядок таблиці метрик із потрібними для підсумку полями."""
    return {"pipeline": pipeline, "stage_name": "s", "image": image, "degradation": degradation,
            "stage": stage, "mse": None, "psnr": None, "ssim": None, "psnr_original": None,
            "ssim_original": None, "iou": iou, "dice": None}


class TestSummaryValues(unittest.TestCase):
    """Перевірка вибору середніх і розкидів."""

    def test_means_and_stds_in_degradation_order(self):
        """IoU 0.6 і 0.8: середнє 0.7, відхилення 0.1414; відсутнє спотворення дає 0."""
        rows = [row("p1", "noise", 2, 0.6, "a00"), row("p1", "noise", 2, 0.8, "b00")]
        summary = analysis.summarize(rows)
        means, stds = plots.summary_values(summary, "p1", 2, "iou", ["noise", "other"])
        self.assertAlmostEqual(means[0], 0.7)
        self.assertAlmostEqual(stds[0], 0.1414, places=4)
        self.assertEqual((means[1], stds[1]), (0, 0))


class TestPairedItems(unittest.TestCase):
    """Перевірка добору парних порівнянь."""

    def test_filters_by_field_and_degradation(self):
        """Лишаються лише рядки потрібної метрики й спотворення."""
        items = [
            {"a": "pipeline1", "b": "pipeline2", "field": "iou", "degradation": "haze",
             "mean": 0.1, "low": 0.0, "high": 0.2},
            {"a": "pipeline1", "b": "pipeline2", "field": "psnr_original", "degradation": "haze",
             "mean": 1.0, "low": 0.5, "high": 1.5},
            {"a": "pipeline1", "b": "pipeline2", "field": "iou", "degradation": "other",
             "mean": 0.3, "low": 0.2, "high": 0.4},
        ]
        result = plots.paired_items(items, "iou", ["haze"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1:], (0.1, 0.0, 0.2))
        self.assertTrue(result[0][0].startswith("П2 - П1"))


class TestFiles(unittest.TestCase):
    """Перевірка створення файлів графіків."""

    def test_grouped_bars_creates_png(self):
        """Згруповані стовпчики зберігаються у непорожній PNG-файл."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "fig.png")
            series = [("a", "#1f77b4", [0.5, 0.7], [0.1, 0.0])]
            plots.grouped_bars(path, ["x", "y"], series, "значення", (0, 1))
            self.assertGreater(os.path.getsize(path), 1000)


if __name__ == "__main__":
    unittest.main()