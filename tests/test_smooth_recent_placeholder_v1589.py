"""Stable waiting and diagnostic placeholders in monitor recent-events card."""
from pathlib import Path
import unittest

MAIN=(Path(__file__).resolve().parents[1]/"app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
class RecentPlaceholderRegression(unittest.TestCase):
    def test_placeholder_present_on_first_render(self):
        block=MAIN.split("private void renderRecentEvents(",1)[1].split("private void fullLogDialog()",1)[0]
        self.assertLess(block.index("if(recent.isEmpty())"),block.index("if(recent.equals(recentRendered))return;"))
        self.assertIn('records.isEmpty()?"Готов к запуску"',block)
        self.assertIn("recentEvents.addView(Ui.text(this,status",block)
    def test_same_placeholder_is_stable(self):
        block=MAIN.split("private void renderRecentEvents(",1)[1].split("private void fullLogDialog()",1)[0]
        self.assertIn("status.equals(recentPlaceholder)",block)
        self.assertIn("recentPlaceholder=status;",block)
        self.assertIn("recentPlaceholder=null;",block)
    def test_manual_journal_follow_untouched(self):
        self.assertIn("journalFollowTail",MAIN)
        self.assertIn("followJournalTail()",MAIN)
if __name__=="__main__": unittest.main()
