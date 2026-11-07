"""Regression checks for exact selected-row deletion, including legacy ID-less sessions."""
from pathlib import Path
import unittest
root=Path(__file__).resolve().parents[1]
store=(root/"app/src/main/java/com/xarkon/pingtest/HistoryStore.java").read_text()
ui=(root/"app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text()
class LegacyHistoryDeleteTest(unittest.TestCase):
    def test_exact_entry_not_id(self):
        self.assertIn("boolean removeEntry(Context c,int index,JSONObject expected)",store)
        self.assertIn("current.toString().equals(expected.toString())",store)
        self.assertIn("if(i!=index)updated.put(old.opt(i))",store)
        self.assertIn("if(expected==null || index<0)return false",store)
        self.assertIn("return false",store)
    def test_ui_uses_selected_index(self):
        history=ui.split("private void historyPage(){",1)[1].split("private TextView historyActionButton(",1)[0]
        self.assertIn("final int historyIndex=i",history)
        self.assertIn("HistoryStore.removeEntry(this,historyIndex,o)",history)
        self.assertNotIn('HistoryStore.remove(this,o.optLong("id"))',history)
if __name__=="__main__":unittest.main()
