"""Автотести читання та підготовки зображень, включно з крайніми випадками."""
import os
import tempfile  # тимчасові папки для тестів: після тесту вони видаляються самі
import unittest  # стандартна бібліотека для автотестів

from PIL import Image

from src import image_io  # модуль, який тестуємо


class TestImageIo(unittest.TestCase):
    """Перевірка функцій модуля image_io."""

    def test_corrupted_and_empty_files_return_none(self):
        """Пошкоджений і порожній файли не призводять до аварії."""
        with tempfile.TemporaryDirectory() as folder:  # тимчасова папка
            bad = os.path.join(folder, "bad.png")  # шлях до "зіпсованого" файлу
            empty = os.path.join(folder, "empty.png")  # шлях до порожнього файлу
            with open(bad, "wb") as file:
                file.write(b"not an image")  # записуємо текст замість зображення
            with open(empty, "wb") as file:
                file.write(b"")  # порожній файл
            # обидва файли мають відкритися як None, без помилки
            self.assertIsNone(image_io.load_image(bad))
            self.assertIsNone(image_io.load_image(empty))

    def test_monochrome_image_is_converted_to_rgb(self):
        """Чорно-біле зображення відкривається як RGB."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "gray.png")
            Image.new("L", (4, 4), 128).save(path)  # "L" - чорно-біле зображення
            self.assertEqual(image_io.load_image(path).mode, "RGB")  # має стати RGB

    def test_square_resize_gives_requested_size(self):
        """Вирізання квадрата й зменшення дають розмір size x size."""
        image = Image.new("RGB", (30, 10))  # прямокутне зображення 30 x 10
        self.assertEqual(image_io.square_resize(image, 5).size, (5, 5))  # очікуємо 5 x 5

    def test_square_resize_takes_the_center(self):
        """Зображення 3x1 з пікселями 10, 20, 30: центральний квадрат 1x1 має колір 20."""
        image = Image.new("RGB", (3, 1))
        for x, value in enumerate((10, 20, 30)):  # три пікселі з різною яскравістю
            image.putpixel((x, 0), (value, value, value))
        # центральний піксель має значення 20
        self.assertEqual(image_io.square_resize(image, 1).getpixel((0, 0)), (20, 20, 20))

    def test_list_images_skips_other_files_and_sorts(self):
        """У списку лише зображення, відсортовані за назвою."""
        with tempfile.TemporaryDirectory() as folder:
            for name in ("b.png", "a.jpg", "notes.txt"):  # два зображення й один текстовий файл
                with open(os.path.join(folder, name), "wb") as file:
                    file.write(b"")
            names = [os.path.basename(path) for path in image_io.list_images(folder)]
            self.assertEqual(names, ["a.jpg", "b.png"])  # notes.txt пропущено

    def test_list_images_missing_folder(self):
        """Неіснуюча папка: порожній список, без помилки."""
        self.assertEqual(image_io.list_images("no_such_folder"), [])


if __name__ == "__main__":
    unittest.main()