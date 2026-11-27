"""Monitor primary action contrast and bounded press-feedback regression."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "app/src/main/java/com/xarkon/pingtest"
MAIN = (JAVA / "MainActivity.java").read_text(encoding="utf-8")
PALETTE = (JAVA / "QrSettingsCards.java").read_text(encoding="utf-8")

class MonitorActionContrastTest(unittest.TestCase):
    def test_monitor_only_style(self):
        self.assertIn("styleMonitorAction(false);", MAIN)
        self.assertIn("styleMonitorAction(s.active);", MAIN)
        style = MAIN.split("private void styleMonitorAction(boolean active){", 1)[1].split("private String fmt", 1)[0]
        self.assertIn("AccentContrast.readableText(fill)", style)
        self.assertIn("new android.graphics.drawable.RippleDrawable(", style)
        self.assertIn("Ui.shape(Color.WHITE,Ui.dp(12),0)", style)
        self.assertIn("go.setTextColor(foreground);", style)
        self.assertIn("go.setOnClickListener(v->toggle());", MAIN)
        self.assertIn("go.setText(s.active?", MAIN)
        history = MAIN.split("private TextView historyActionButton(", 1)[1].split("private void historyDetails(", 1)[0]
        self.assertIn("Ui.button(this,title,filled)", history)
        self.assertNotIn("styleMonitorAction", history)

    @unittest.skipUnless(shutil.which("javac") and shutil.which("java"), "JDK required")
    def test_actual_java_contrast_for_palette_and_rgb_grid(self):
        palette = PALETTE.split("int[] ACCENTS={", 1)[1].split("};", 1)[0]
        colors = re.findall(r"0x[0-9a-fA-F]{8}", palette)
        self.assertGreaterEqual(len(colors), 24)
        harness = """
package com.xarkon.pingtest;
public final class ContrastHarness {
    private static void verify(int fill) {
        int text = AccentContrast.readableText(fill);
        if (AccentContrast.contrast(fill,text) < 4.5)
            throw new AssertionError(Integer.toHexString(fill));
    }
    public static void main(String[] args) {
        int[] colors = {""" + ",".join(colors) + """};
        for (int fill : colors) verify(fill);
        for (int r=0;r<256;r+=15)
            for (int g=0;g<256;g+=15)
                for (int b=0;b<256;b+=15)
                    verify(0xff000000|(r<<16)|(g<<8)|b);
        if (AccentContrast.readableText(0xff8773e4) != 0xff071219)
            throw new AssertionError("Violet accent must use dark ink");
        if (AccentContrast.readableText(0xff000000) != 0xffffffff)
            throw new AssertionError("Black fill must use white");
    }
}
"""
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            source = out / "ContrastHarness.java"
            source.write_text(harness, encoding="utf-8")
            subprocess.run(["javac", "-d", str(out), str(JAVA / "AccentContrast.java"), str(source)], check=True)
            subprocess.run(["java", "-cp", str(out), "com.xarkon.pingtest.ContrastHarness"], check=True)

if __name__ == "__main__":
    unittest.main()
