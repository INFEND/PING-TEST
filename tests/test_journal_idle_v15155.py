from pathlib import Path
import unittest

MAIN = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
METHOD = MAIN.split("private void refreshJournal(){", 1)[1].split("// HISTORY", 1)[0]

class JournalIdle(unittest.TestCase):
    def test_idle_fast_paths_precede_search_and_view_mutation(self):
        guard = METHOD.index("if(snapshot.id==journalSessionId)")
        empty = METHOD.index("if(records.isEmpty()&&journalTail==null&&journalRows.getChildCount()==0)return;")
        unchanged = METHOD.index("if(!records.isEmpty()&&journalTail==records.get(records.size()-1))return;")
        search = METHOD.index("records.lastIndexOf(journalTail)")
        self.assertLess(guard, empty)
        self.assertLess(empty, unchanged)
        self.assertLess(unchanged, search)
        self.assertLess(search, METHOD.index("journalRows.removeAllViews()"))

    def test_session_change_still_rebuilds(self):
        self.assertIn("if(snapshot.id!=journalSessionId||tailIndex<0)", METHOD)
        self.assertIn("journalSessionId=snapshot.id;", METHOD)

if __name__ == "__main__":
    unittest.main()
