"""Автотести порівняння пайплайнів."""
import math
import unittest

from src import comparison


def row(image, value, pipeline="p1", stage=1, degradation="noise"):
    """Рядок таблиці метрик із одним значенням iou."""
    return {"image": image, "pipeline": pipeline, "stage": stage,
            "degradation": degradation, "iou": value}


class TestClassName(unittest.TestCase):
    """Перевірка назви класу."""

    def test_class_name(self):
        """Номер знімка відкидається."""
        self.assertEqual(comparison.class_name("forest05"), "forest")


class TestSelectAndByClass(unittest.TestCase):
    """Перевірка вибору рядків і середніх за класами."""

    def test_select_filters(self):
        """Лишаються рядки потрібного пайплайна, стадії й спотворення."""
        rows = [row("a00", 1), row("a01", 2, pipeline="p2"), row("a02", 3, stage=2),
                row("a03", 4, degradation="other")]
        self.assertEqual(len(comparison.select(rows, "p1", 1)), 2)
        self.assertEqual(len(comparison.select(rows, "p1", 1, "noise")), 1)

    def test_by_class_means(self):
        """forest: (0.8 + 0.6) / 2 = 0.7, river: 0.5."""
        rows = [row("forest00", 0.8), row("forest01", 0.6), row("river00", 0.5)]
        result = comparison.by_class(rows, "p1", 1, "iou")
        self.assertAlmostEqual(result["forest"][0], 0.7)
        self.assertEqual(result["forest"][1], 2)
        self.assertAlmostEqual(result["river"][0], 0.5)


class TestPaired(unittest.TestCase):
    """Перевірка парного порівняння."""

    def test_differences_and_wins(self):
        """Різниці 0.1 і 0.2: середнє 0.15, відхилення 0.0707, інтервал 0.15 +- 0.098."""
        rows_a = [row("x00", 0.5), row("x01", 0.7)]
        rows_b = [row("x00", 0.6), row("x01", 0.9)]
        result = comparison.paired(rows_a, rows_b, "iou")
        self.assertEqual(result["n"], 2)
        self.assertAlmostEqual(result["mean"], 0.15)
        self.assertAlmostEqual(result["high"] - result["mean"], 0.098, places=3)
        self.assertEqual(result["wins"], 1.0)

    def test_worse_counts_as_no_win(self):
        """Якщо b гірше за a в одному зі знімків, частка перемог 0.5."""
        rows_a = [row("x00", 0.5), row("x01", 0.7)]
        rows_b = [row("x00", 0.6), row("x01", 0.4)]
        self.assertEqual(comparison.paired(rows_a, rows_b, "iou")["wins"], 0.5)

    def test_missing_infinite_and_unmatched_are_ignored(self):
        """Порожні, нескінченні значення й знімки без пари не враховуються."""
        rows_a = [row("x00", 0.5), row("x01", None), row("x02", math.inf), row("x03", 0.3)]
        rows_b = [row("x00", 0.7), row("x01", 0.9), row("x02", 0.9), row("x04", 0.9)]
        result = comparison.paired(rows_a, rows_b, "iou")
        self.assertEqual(result["n"], 1)
        self.assertAlmostEqual(result["mean"], 0.2)

    def test_no_common_images_gives_none(self):
        """Без спільних знімків порівняння неможливе."""
        self.assertIsNone(comparison.paired([row("a00", 1)], [row("b00", 1)], "iou"))


if __name__ == "__main__":
    unittest.main()
