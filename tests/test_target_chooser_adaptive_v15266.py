import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = (ROOT / "app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")

class TargetChooserAdaptiveTextTest(unittest.TestCase):
    def test_custom_name_is_bounded_without_changing_target_value(self):
        self.assertIn('Ui.text(this,target.name,14,Ui.fg(),true)', SRC)
        self.assertIn('targetName.setSingleLine(true)', SRC)
        self.assertIn('targetName.setEllipsize(TextUtils.TruncateAt.END)', SRC)
        self.assertIn('targetName.setAutoSizeTextTypeUniformWithConfiguration(11,14,1,android.util.TypedValue.COMPLEX_UNIT_SP)', SRC)
        self.assertRegex(SRC, r'labels.addView\(targetName\);')
        self.assertIn('sub.setMaxLines(2)', SRC)
        self.assertIn('sub.setEllipsize(TextUtils.TruncateAt.END)', SRC)
        self.assertIn('edit.setOnClickListener(v->{dialog.dismiss();editTarget(target);});', SRC)
        self.assertIn('row.setOnClickListener(v->{dialog.dismiss();selectTarget(target);});', SRC)

if __name__ == "__main__":
    unittest.main()
