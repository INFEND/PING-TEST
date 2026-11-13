from pathlib import Path
import unittest
SRC=(Path(__file__).resolve().parents[1]/"app/src/main/java/com/xarkon/pingtest/HistoryStore.java").read_text(encoding="utf-8")
class HistoryPosition(unittest.TestCase):
    def test_existing_checkpoint_replaces_in_place(self):
        body=SRC.split("void upsert(",1)[1].split("static boolean isStaleCheckpoint",1)[0]
        self.assertIn("if(existingIndex<0)updated.put(entry);",body)
        self.assertIn("if(i==existingIndex)updated.put(entry);",body)
        self.assertLess(body.index("isStaleCheckpoint(previous,entry)"),body.index("if(existingIndex<0)"))
    def test_limit_read_once(self):
        body=SRC.split("void upsert(",1)[1].split("static boolean isStaleCheckpoint",1)[0]
        self.assertEqual(body.count("limit(c)"),1)
        self.assertIn("updated.length() < maxEntries",body)
if __name__=="__main__": unittest.main()
