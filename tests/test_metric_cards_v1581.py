"""Check themed three-column statistics and update dialog contrast."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]/"app/src/main/java/com/xarkon/pingtest"

class MetricCardsRegression(unittest.TestCase):
    def test_three_cells_and_actual_average(self):
        code=(ROOT/"MainActivity.java").read_text(encoding="utf-8")
        for label in ("МИН","СРЕД","МАКС"):
            self.assertIn('detailStat(detail,"'+label+'")',code)
        self.assertIn('middleText.setText(s.timed==0?"—":fmt(s.avg())+" мс")',code)
        self.assertIn('bestText.setText(s.timed==0?"—":fmt(s.min)+" мс")',code)
        self.assertIn('maxText.setText(s.timed==0?"—":fmt(s.max)+" мс")',code)
        self.assertNotIn("jitterText",code)

    def test_ota_uses_selected_palette(self):
        code=(ROOT/"OtaProgressDialog.java").read_text(encoding="utf-8")
        self.assertIn('Ui.applyPalette(a)',code)
        self.assertIn('panel=Ui.surface(a)',code)
        self.assertIn('Ui.onAccent(a)',code)

if __name__=="__main__":
    unittest.main()
