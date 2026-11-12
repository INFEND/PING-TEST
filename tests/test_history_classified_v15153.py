from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]/"app/src/main/java/com/xarkon/pingtest"
MAIN=(ROOT/"MainActivity.java").read_text(encoding="utf-8")
SERVICE=(ROOT/"PingService.java").read_text(encoding="utf-8")

class HistoryClassifiedTests(unittest.TestCase):
    def test_saved_loss_takes_precedence(self):
        self.assertIn('lost=o.has("lost")?Math.max(0,lost):Math.max(0,completed-ok)',MAIN)
        self.assertIn('obj.has("lost")?Math.max(0,obj.optInt("lost"))',MAIN)
        self.assertIn('completed=Math.max(0,ok)+lost;',MAIN)
        self.assertIn('completed=ok+lost;',MAIN)
    def test_unknown_notification(self):
        self.assertIn('if(s.sent>0&&classified==0)content=routeLabel+" · ожидание · потери —";',SERVICE)
    def test_history_unknown_and_bounded(self):
        self.assertIn('confirmedLoss?"НЕТ ОТВЕТА":"НЕТ ДАННЫХ"',MAIN)
        self.assertIn('fmt(o.optDouble("avg"))+" мс":"<1 мс"',MAIN)
