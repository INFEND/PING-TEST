import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
ACTIVITY = (ROOT / "app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
SERVICE = (ROOT / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class PendingDisplayTests(unittest.TestCase):
    def test_pending_requests_do_not_show_red_quality(self):
        self.assertIn("ms<0?(s.lost>0?QualityColors.RED:QualityColors.UNKNOWN)", ACTIVITY)
        self.assertNotIn("ms<0?(s.sent>0?QualityColors.RED:QualityColors.UNKNOWN)", ACTIVITY)
    def test_notification_does_not_show_negative_latency(self):
        self.assertIn('s.timed>0?String.format(Locale.US,"%.0f мс",s.avg()):s.ok>0?"<1 мс":"ожидание"', SERVICE)
        self.assertNotIn('routeLabel,s.ok,classified,s.avg(),s.lossPct()', SERVICE)

if __name__ == "__main__":
    unittest.main()
