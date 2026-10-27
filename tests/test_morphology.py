"""Автотести морфології на масках 5x5 з результатами, обчисленими вручну."""
import unittest

from PIL import Image

from src import morphology


def mask_from_points(white_points, size=5):
    """Маска size x size: пікселі з переліку (x, y) білі, решта чорні."""
    image = Image.new("RGB", (size, size), (0, 0, 0))
    for point in white_points:
        image.putpixel(point, (255, 255, 255))
    return image


def block_points():
    """Білий квадрат 3x3 у центрі маски 5x5."""
    return [(x, y) for x in range(1, 4) for y in range(1, 4)]


def white_set(image):
    """Множина координат білих пікселів маски."""
    width, height = image.size
    return {(x, y) for x in range(width) for y in range(height)
            if image.getpixel((x, y))[0] == 255}


class TestMorphology(unittest.TestCase):
    """Перевірка ерозії, дилатації, відкриття й закриття."""

    def test_erosion_of_block_leaves_center(self):
        """Ерозія квадрата 3x3 залишає лише центральний піксель."""
        result = morphology.erode(mask_from_points(block_points()), 1)
        self.assertEqual(white_set(result), {(2, 2)})

    def test_dilation_of_point_gives_block(self):
        """Дилатація одного пікселя дає квадрат 3x3."""
        result = morphology.dilate(mask_from_points([(2, 2)]), 1)
        self.assertEqual(white_set(result), set(block_points()))

    def test_opening_removes_isolated_speck(self):
        """Відкриття прибирає окремий білий піксель."""
        result = morphology.opening(mask_from_points([(2, 2)]), 1)
        self.assertEqual(white_set(result), set())

    def test_opening_keeps_block(self):
        """Відкриття не змінює квадрат 3x3."""
        result = morphology.opening(mask_from_points(block_points()), 1)
        self.assertEqual(white_set(result), set(block_points()))

    def test_closing_fills_hole(self):
        """Закриття заповнює чорну дірку в білій області."""
        points = [(x, y) for x in range(5) for y in range(5) if (x, y) != (2, 2)]
        result = morphology.closing(mask_from_points(points), 1)
        self.assertEqual(len(white_set(result)), 25)

    def test_erosion_does_not_eat_the_border(self):
        """Повністю біла маска не змінюється: край не з'їдається."""
        points = [(x, y) for x in range(5) for y in range(5)]
        result = morphology.erode(mask_from_points(points), 1)
        self.assertEqual(len(white_set(result)), 25)

    def test_clean_mask_removes_speck_and_fills_hole(self):
        """Блок 7x7 із діркою в центрі й пляма в куті: пляма зникає, блок стає суцільним."""
        block = {(x, y) for x in range(2, 9) for y in range(2, 9)}
        points = (block - {(5, 5)}) | {(0, 0)}
        result = morphology.clean_mask(mask_from_points(sorted(points), size=11), 1)
        self.assertEqual(white_set(result), block)

    def test_opening_destroys_thin_ring(self):
        """Тонке кільце завтовшки в піксель відкриттям зникає: воно вужче за вікно 3x3."""
        ring = set(block_points()) - {(2, 2)}
        result = morphology.opening(mask_from_points(sorted(ring)), 1)
        self.assertEqual(white_set(result), set())


if __name__ == "__main__":
    unittest.main()