"""Автотести метрик масок на зображеннях 3x3 з результатами, обчисленими вручну."""
import unittest

from PIL import Image

from src import mask_metrics


def mask_from_indexes(white_indexes):
    """Маска 3x3: пікселі з указаними номерами (0..8, рядок за рядком) білі, решта чорні."""
    image = Image.new("RGB", (3, 3), (0, 0, 0))
    for index in white_indexes:
        image.putpixel((index % 3, index // 3), (255, 255, 255))
    return image


class TestMaskMetrics(unittest.TestCase):
    """Перевірка IoU і коефіцієнта Дайса."""

    def test_iou_partial_overlap(self):
        """Білі пікселі {0,1,2,3} і {2,3,4,5,6}: перетин {2,3} = 2, об'єднання 0..6 = 7.
        IoU = 2 / 7 = 0.2857.
        """
        mask_a = mask_from_indexes([0, 1, 2, 3])
        mask_b = mask_from_indexes([2, 3, 4, 5, 6])
        self.assertAlmostEqual(mask_metrics.iou(mask_a, mask_b), 2 / 7, places=4)

    def test_dice_partial_overlap(self):
        """Ті самі маски: Дайс = 2 * 2 / (4 + 5) = 4 / 9 = 0.4444."""
        mask_a = mask_from_indexes([0, 1, 2, 3])
        mask_b = mask_from_indexes([2, 3, 4, 5, 6])
        self.assertAlmostEqual(mask_metrics.dice(mask_a, mask_b), 4 / 9, places=4)

    def test_identical_masks_give_one(self):
        """Однакові маски: IoU = 1 і Дайс = 1."""
        mask = mask_from_indexes([1, 4, 7])
        self.assertEqual(mask_metrics.iou(mask, mask), 1.0)
        self.assertEqual(mask_metrics.dice(mask, mask), 1.0)

    def test_disjoint_masks_give_zero(self):
        """Білі області не перетинаються: IoU = 0."""
        self.assertEqual(mask_metrics.iou(mask_from_indexes([0, 1]), mask_from_indexes([7, 8])), 0)

    def test_two_empty_masks_give_one(self):
        """Дві повністю чорні маски вважаються однаковими: IoU = 1."""
        self.assertEqual(mask_metrics.iou(mask_from_indexes([]), mask_from_indexes([])), 1.0)

    def test_different_sizes_raise(self):
        """Маски різного розміру: ValueError."""
        with self.assertRaises(ValueError):
            mask_metrics.iou(mask_from_indexes([0]), Image.new("RGB", (4, 4)))


if __name__ == "__main__":
    unittest.main()
