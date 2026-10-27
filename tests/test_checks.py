"""Автотести перевірки еталонних сценаріїв."""
import unittest

from src import checks


def degraded(image, psnr):
    """Рядок таблиці спотворених знімків."""
    return {"image": image, "degradation": "noise", "psnr": psnr}


def metric(image, psnr_original, stage=1, iou=None):
    """Рядок таблиці метрик пайплайна p1."""
    return {"image": image, "pipeline": "p1", "stage": stage, "degradation": "noise",
            "psnr_original": psnr_original, "iou": iou}


DEGRADED = [degraded("a00", 20), degraded("b00", 20), degraded("c00", 20)]
GAIN_ROWS = [metric("a00", 22), metric("b00", 20.5), metric("c00", 25)]


class TestGainCount(unittest.TestCase):
    """Перевірка підрахунку знімків із приростом PSNR."""

    def test_two_of_three_pass(self):
        """Прирости 2, 0.5 і 5 дБ: поріг 1 дБ проходять 2 із 3."""
        self.assertEqual(checks.gain_count(GAIN_ROWS, DEGRADED, "noise", 1.0), (2, 3))

    def test_image_without_degraded_row_is_skipped(self):
        """Знімок без спотвореної копії в таблиці не враховується."""
        rows = GAIN_ROWS + [metric("d00", 30)]
        self.assertEqual(checks.gain_count(rows, DEGRADED, "noise", 1.0), (2, 3))


class TestRunScenarios(unittest.TestCase):
    """Перевірка сценаріїв."""

    def gain_scenario(self, min_share):
        """Сценарій приросту з порогом частки знімків."""
        return {"id": 1, "kind": "gain", "pipelines": ["p1"], "degradation": "noise",
                "min_gain": 1.0, "min_share": min_share}

    def test_gain_scenario_passes(self):
        """Частка 2/3 = 0.667 не менша за 0.6: тест-кейс пройдено."""
        cases = checks.run_scenarios(GAIN_ROWS, DEGRADED, [self.gain_scenario(0.6)],
                                     {"p1": 1}, ["noise"])
        self.assertTrue(cases[0]["ok"])
        self.assertAlmostEqual(cases[0]["value"], 2 / 3)

    def test_gain_scenario_fails(self):
        """Частка 2/3 менша за 0.7: тест-кейс не пройдено."""
        cases = checks.run_scenarios(GAIN_ROWS, DEGRADED, [self.gain_scenario(0.7)],
                                     {"p1": 1}, ["noise"])
        self.assertFalse(cases[0]["ok"])

    def test_mean_scenario(self):
        """Середній IoU двох знімків (0.6 і 0.8) дорівнює 0.7: поріг 0.69 проходить, 0.71 ні."""
        rows = [metric("a00", None, stage=2, iou=0.6), metric("b00", None, stage=2, iou=0.8)]
        for min_mean, expected in ((0.69, True), (0.71, False)):
            scenario = {"id": 4, "kind": "mean", "pipelines": ["p1"], "field": "iou",
                        "min_mean": min_mean}
            cases = checks.run_scenarios(rows, DEGRADED, [scenario], {"p1": 2}, ["noise"])
            self.assertEqual(cases[0]["ok"], expected)

    def test_missing_data_is_not_passed(self):
        """Без даних про пайплайн тест-кейс не вважається пройденим."""
        scenario = {"id": 4, "kind": "mean", "pipelines": ["p2"], "field": "iou", "min_mean": 0.1}
        cases = checks.run_scenarios(GAIN_ROWS, DEGRADED, [scenario], {"p2": 2}, ["noise"])
        self.assertFalse(cases[0]["ok"])

    def test_count_passed(self):
        """Підрахунок пройдених тест-кейсів."""
        cases = [{"ok": True}, {"ok": False}, {"ok": True}]
        self.assertEqual(checks.count_passed(cases), (2, 3))


if __name__ == "__main__":
    unittest.main()