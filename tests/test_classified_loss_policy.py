import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SERVICE = (ROOT / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")
MAIN = (ROOT / "app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")

class ClassifiedLossTests(unittest.TestCase):
    def test_only_classified_probes_are_denominator(self):
        self.assertIn("int classified=ok+lost;", SERVICE)
        self.assertIn("classified==0?0:100.0*lost/classified", SERVICE)
        self.assertNotIn("Math.max(0,done-ok)/done", SERVICE)

    def test_fatal_execution_error_is_not_packet_loss(self):
        self.assertIn("else if(fatal){live.error=error;", SERVICE)
        self.assertIn("else{live.lost++;", SERVICE)
        self.assertIn("live.done++;", SERVICE)

    def test_no_reply_label_requires_confirmed_loss(self):
        self.assertIn('s.lost>0?"НЕТ ОТВЕТА":"ОЖИДАНИЕ"', MAIN)
        self.assertIn("s.ok==0&&s.lost>0&&s.error.isEmpty()", SERVICE)

    def test_notification_uses_classified_denominator(self):
        self.assertIn("int classified=s.ok+s.lost;", SERVICE)
        self.assertIn('routeLabel,s.ok,classified,s.timed>0?String.format(Locale.US,"%.0f мс",s.avg()):s.ok>0?"<1 мс":"ожидание",s.lossPct()', SERVICE)
        self.assertNotIn("routeLabel,s.ok,classified,s.avg(),s.lossPct()", SERVICE)
        self.assertNotIn("s.ok,s.sent,s.avg()", SERVICE)

    def test_history_persists_distinct_outcomes(self):
        for field in ("sent", "done", "ok", "lost", "skipped"):
            self.assertIn('j.put("'+field+'",s.'+field+')', SERVICE)

if __name__ == "__main__":
    unittest.main()
