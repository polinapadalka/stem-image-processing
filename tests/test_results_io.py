"""Автотести запису результатів у CSV."""
import csv  # для читання записаного файлу назад
import math
import os
import tempfile  # тимчасова папка, яка сама видаляється після тесту
import unittest

from src import results_io


def read_rows(path):
    """Читає CSV-файл і повертає список словників."""
    with open(path, "r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


class TestResultsIo(unittest.TestCase):
    """Перевірка запису CSV."""

    def test_rows_are_written_and_read_back(self):
        """Записані рядки читаються назад із тими самими значеннями."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "table.csv")
            rows = [{"image": "a", "mse": 1.5}, {"image": "b", "mse": 2.5}]
            results_io.write_csv(path, rows, ["image", "mse"])
            result = read_rows(path)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[1]["image"], "b")
            self.assertEqual(float(result[0]["mse"]), 1.5)

    def test_missing_folder_is_created(self):
        """Якщо папки немає, вона створюється."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "new_folder", "table.csv")
            results_io.write_csv(path, [{"x": 1}], ["x"])
            self.assertTrue(os.path.exists(path))

    def test_empty_rows_write_only_header(self):
        """Без рядків у файлі лише назви стовпців."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "table.csv")
            results_io.write_csv(path, [], ["image", "mse"])
            with open(path, "r", encoding="utf-8") as file:
                self.assertEqual(file.read().strip(), "image,mse")

    def test_infinity_is_written_as_inf(self):
        """Нескінченний PSNR (однакові зображення) записується як inf."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "table.csv")
            results_io.write_csv(path, [{"psnr": math.inf}], ["psnr"])
            self.assertEqual(read_rows(path)[0]["psnr"], "inf")


if __name__ == "__main__":
    unittest.main()
