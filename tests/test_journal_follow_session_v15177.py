from pathlib import Path
import unittest

MAIN=(Path(__file__).resolve().parents[1]/"app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")

class JournalFollowSession(unittest.TestCase):
    def test_posted_follow_checks_window_and_session(self):
        method=MAIN.split("private void refreshJournal(){",1)[1].split("// HISTORY",1)[0]
        self.assertIn("final ScrollView postedScroll=journalScroll;",method)
        self.assertIn("final long postedSession=journalSessionId;",method)
        self.assertIn("journalScroll==postedScroll&&journalSessionId==postedSession",method)
        self.assertIn("journalDialog!=null&&journalDialog.isShowing())followJournalTail();",method)

    def test_rebuild_cancels_old_animation(self):
        self.assertIn("if(snapshot.id!=journalSessionId||tailIndex<0){\n            stopJournalScrollAnimation();\n            journalRows.removeAllViews();",MAIN)

if __name__=="__main__":
    unittest.main()
