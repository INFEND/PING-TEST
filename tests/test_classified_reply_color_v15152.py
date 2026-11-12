"""Live packet counters use only classified outcomes for quality."""
from pathlib import Path
import unittest

SRC = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")

class ClassifiedReplyColor(unittest.TestCase):
    def test_pending_and_skipped_are_not_losses(self):
        self.assertIn("sendText.update(s.ok,s.sent,s.lost,sameSession)", SRC)
        self.assertIn("QualityColors.success(nextOk,nextOk+lost)", SRC)
        self.assertNotIn("QualityColors.success(nextOk,nextSent)", SRC)

    def test_classification_refreshes_color_without_new_send(self):
        self.assertIn("lost==targetLost", SRC)
        self.assertIn("targetLost=lost", SRC)

    def test_no_classified_outcome_has_unknown_loss(self):
        self.assertIn("failed.update(s.ok+s.lost==0?-1:s.lossPct()", SRC)
