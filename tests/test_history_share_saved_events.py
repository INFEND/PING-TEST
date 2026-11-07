"""Regression: shared history includes only genuinely persisted events."""
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          "app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
HISTORY = SOURCE.split("private void historyDetails(JSONObject obj)", 1)[1].split("private String date(", 1)[0]


class HistoryShareSavedEventsTests(unittest.TestCase):
    def test_saved_events_are_exported(self):
        for fragment in (
            'obj.optJSONArray("events")',
            'for(int i=0;i<savedEvents.length();i++)',
            'event.optInt("number",0)',
            'event.optDouble("latencyMs",-1)',
            'event.optString("message","")',
            'String out=report.toString()',
            'copyButton.setOnClickListener(v->copy(out))',
            'shareButton.setOnClickListener(v->share(out))',
        ):
            self.assertIn(fragment, HISTORY)

    def test_legacy_and_missing_history_are_honest(self):
        self.assertIn('else if(!rawLog.trim().isEmpty())', HISTORY)
        self.assertIn('report.append("\\n").append(rawLog)', HISTORY)
        self.assertIn('События этого сеанса не сохранены.', HISTORY)


if __name__ == "__main__":
    unittest.main()
