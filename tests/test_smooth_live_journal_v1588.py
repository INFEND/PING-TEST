"""Regressions for continuous journal follow and stable recent packet rows."""
from pathlib import Path
import unittest

MAIN=(Path(__file__).resolve().parents[1]/"app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")

class JournalSmoothness(unittest.TestCase):
    def test_no_discontinuous_forced_bottom_scroll(self):
        method=MAIN.split("private void refreshJournal(){",1)[1].split("// HISTORY",1)[0]
        self.assertNotIn("fullScroll(View.FOCUS_DOWN)",method)
        self.assertIn("followJournalTail()",method)
        self.assertIn("removedHeight",method)
        self.assertIn("journalScroll.getScrollY()-removedHeight",method)

    def test_animation_retargets_without_cancel_each_probe(self):
        method=MAIN.split("private void followJournalTail(){",1)[1].split("private void refreshJournal(){",1)[0]
        self.assertIn("journalTargetScroll=",method)
        self.assertIn("journalScrollAnimation!=null&&journalScrollAnimation.isRunning()",method)
        self.assertIn("journalLastFrame",method)
        self.assertIn("Math.exp(-frame/145.0)",method)
        self.assertIn("journalScroll.scrollTo(0,position+step)",method)

    def test_manual_scroll_stops_follow_without_consuming_touches(self):
        self.assertIn("journalUserTouching=true;journalFollowTail=false;",MAIN)
        self.assertIn("stopJournalScrollAnimation();",MAIN)
        self.assertIn("return false; // Never interfere with normal manual scrolling/fling.",MAIN)
        self.assertIn("scroll.setOnScrollChangeListener",MAIN)

    def test_recent_packets_do_not_recreate_unchanged_rows(self):
        code=MAIN.split("private void renderRecentEvents(",1)[1].split("private void fullLogDialog()",1)[0]
        self.assertIn("recent.equals(recentRendered)",code)
        self.assertIn("overlap",code)
        self.assertIn("row.animate().alpha(1f)",code)
        self.assertIn("recentRendered.addAll(recent)",code)

if __name__=="__main__":
    unittest.main()
