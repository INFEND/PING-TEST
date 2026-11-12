"""Live RTT and loss text must display measured values, not animation frames."""
from pathlib import Path
import unittest

class LiveMetricAccuracy(unittest.TestCase):
    def test_color_only_interpolation(self):
        source = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
        metric = source.split("private final class Metric extends TextView", 1)[1].split("private void checkClipboard", 1)[0]
        self.assertIn('shown=next;setText(fmt(next)', metric)
        self.assertIn('a.addUpdateListener(v->setTextColor(QualityColors.blend', metric)
        self.assertNotIn('fmt(shown)', metric)
        self.assertIn('!Double.isFinite(next)', metric)
        self.assertIn('if(next==-2 && kind==0)', metric)

if __name__ == "__main__":
    unittest.main()
