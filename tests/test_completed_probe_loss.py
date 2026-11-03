import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
SERVICE=(ROOT/"app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")
MAIN=(ROOT/"app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")

class CompletedProbeLossTests(unittest.TestCase):
    def test_live_loss_does_not_count_inflight_requests(self):
        self.assertIn("int classified=ok+lost;",SERVICE)
        self.assertIn("classified==0?0:100.0*lost/classified",SERVICE)
        self.assertNotIn("return done==0?0:100.0*Math.max(0,done-ok)/done;",SERVICE)
        self.assertNotIn("Math.max(0,sent-ok)/sent;",SERVICE)
    def test_history_preserves_real_counters(self):
        self.assertIn('j.put("done",s.done)',SERVICE)
        self.assertIn('j.put("lost",s.lost)',SERVICE)
        self.assertIn('j.put("skipped",s.skipped)',SERVICE)
    def test_history_compatibility(self):
        self.assertIn('o.has("done")?o.optInt("done"):sent',MAIN)
        self.assertIn('obj.has("done")?obj.optInt("done"):sent',MAIN)
    def test_live_ui_uses_snapshot_loss(self):
        self.assertIn("s.lossPct()",MAIN)

if __name__=="__main__":
    unittest.main()
