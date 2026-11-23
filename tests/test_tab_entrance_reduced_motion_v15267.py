import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = (ROOT / "app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")

class TabEntranceReducedMotionTests(unittest.TestCase):
    def test_tab_entrance_respects_android_animation_disable(self):
        start = SRC.index("private void showTab(int next)")
        end = SRC.index("private void header()", start)
        body = SRC[start:end]
        self.assertIn('if(!noEntrance&&AppPrefs.bool(this,"motion",true)&&ValueAnimator.areAnimatorsEnabled()){', body)
        self.assertIn('page.animate().alpha(1).translationY(0)', body)
        self.assertIn('page.setAlpha(.45f)', body)
        self.assertIn('page.setTranslationY(Ui.dp(7))', body)

    def test_ping_values_and_service_not_touched_by_ui_change(self):
        self.assertIn('if(tab==0)pingPage();else if(tab==1)historyPage();else settingsPage();', SRC)

if __name__ == "__main__":
    unittest.main()
