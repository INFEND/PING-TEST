"""Regression: historical report actions never wrap or clip on narrow screens."""
from pathlib import Path
import unittest

SOURCE=(Path(__file__).resolve().parents[1]/"app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")

class HistoryReportActionRegression(unittest.TestCase):
    def test_single_line_and_font_resize(self):
        helper=SOURCE.split("private TextView historyActionButton(",1)[1].split("private void historyDetails(",1)[0]
        self.assertIn("button.setSingleLine(true)",helper)
        self.assertIn("setAutoSizeTextTypeUniformWithConfiguration(",helper)
        self.assertIn("button.setEllipsize(TextUtils.TruncateAt.END)",helper)

    def test_actions_are_not_three_44dp_columns(self):
        report=SOURCE.split("private void historyDetails(JSONObject obj){",1)[1].split("private static String routeLabelFromInfo(",1)[0]
        for label in ("КОПИРОВАТЬ","ПОДЕЛИТЬСЯ","ЗАКРЫТЬ"):
            self.assertIn(f'historyActionButton("{label}"',report)
        self.assertIn("boolean stackButtons=",report)
        self.assertIn("screenWidthDp<360",report)
        self.assertIn("fontScale>1.25f",report)
        self.assertIn("actions.addView(closeButton,Ui.margins(-1,48,8,0))",report)
        self.assertNotIn("actions.addView(copyButton,new LinearLayout.LayoutParams(0,Ui.dp(44),1))",report)
        for action in ("copy(out)","share(out)","dialog.dismiss()"):
            self.assertIn(action,report)

if __name__=="__main__":
    unittest.main()
