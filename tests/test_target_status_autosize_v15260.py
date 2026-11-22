#!/usr/bin/env python3
"""UI regression: long target status stays legible and live text remains unchanged."""
from pathlib import Path
s = Path("app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
page = s.split("private void pingPage(){", 1)[1].split("private void miniMetric(", 1)[0]
assert 'ip=Ui.text(this,"Готов к проверке",11,Ui.muted(),false)' in page
assert "ip.setSingleLine(true);ip.setEllipsize(TextUtils.TruncateAt.END);" in page
assert "ip.setAutoSizeTextTypeUniformWithConfiguration(9,11,1,android.util.TypedValue.COMPLEX_UNIT_SP)" in page
assert "target.addView(ip,Ui.margins(-1,-2,0,9))" in page
assert "ip.setText(s.active||s.done>0?" in s
assert "ip.setContentDescription(" not in page
gradle = Path("app/build.gradle").read_text(encoding="utf-8")
assert int(gradle.split("versionCode ",1)[1].split()[0]) >= 268
print("PASS: target status auto-size, live text and layout preserved")
