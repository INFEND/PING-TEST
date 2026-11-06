"""Regression checks for user-facing monitor status labels."""
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          "app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")


class RussianMonitorStatusTests(unittest.TestCase):
    def test_status_labels_are_russian(self):
        for label in ('● РАБОТАЕТ', '● ОШИБКА', '● ГОТОВ'):
            self.assertIn(label, SOURCE)
        for label in ('● LIVE', '● ERROR'):
            self.assertNotIn(label, SOURCE)

    def test_route_indicator_is_compact(self):
        self.assertIn('● БЕЗ VPN', SOURCE)
        self.assertIn('● ЧЕРЕЗ VPN', SOURCE)
        self.assertNotIn('СЕТЬ  •  ', SOURCE)

    def test_critical_network_warnings_remain(self):
        self.assertIn('МАРШРУТ  •  ', SOURCE)
        self.assertIn('ВНИМАНИЕ  •  ', SOURCE)


if __name__ == "__main__":
    unittest.main()
