import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MAIN = ROOT / "app/src/main/java/com/xarkon/pingtest/MainActivity.java"

class RouteLabelRegression(unittest.TestCase):
    def test_history_and_monitor_share_route_classification(self):
        source = MAIN.read_text(encoding="utf-8")
        self.assertIn("String routeLabel=routeLabelFromInfo(vpnInfo);", source)
        self.assertIn("String routeLabel=routeLabelFromInfo(route);", source)
        self.assertIn('"● "+routeLabelFromInfo(s.vpnInfo)', source)

    def test_unknown_is_not_mislabeled_direct(self):
        source = MAIN.read_text(encoding="utf-8")
        start = source.index("private static String routeLabelFromInfo(")
        end = source.index("private String date(", start)
        helper = source[start:end]
        self.assertIn('value.contains("не определ")', helper)
        self.assertIn('value.contains("без vpn")', helper)
        self.assertIn('return "МАРШРУТ НЕИЗВЕСТЕН";', helper)
        self.assertNotIn('info.isEmpty()?"МАРШРУТ НЕИЗВЕСТЕН":"БЕЗ VPN"', source)

if __name__ == "__main__":
    unittest.main()
