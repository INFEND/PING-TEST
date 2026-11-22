#!/usr/bin/env python3
"""UI regression: selected target name scales on narrow displays without changing behavior."""
from pathlib import Path
s = Path("app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
page = s.split("private void pingPage(){", 1)[1].split("private void ", 1)[0]
assert "host=Ui.text(this,TargetStore.selected(this).name,22,Ui.fg(),true)" in page
assert "host.setSingleLine(true);host.setEllipsize(TextUtils.TruncateAt.END);" in page
assert "host.setAutoSizeTextTypeUniformWithConfiguration(12,22,1,android.util.TypedValue.COMPLEX_UNIT_SP)" in page
assert "row.setOnClickListener(v->chooseHost())" in page
assert "target.setOnClickListener(v->chooseHost())" in page
assert "ip.setSingleLine(true);ip.setEllipsize(TextUtils.TruncateAt.END)" in page
gradle=Path("app/build.gradle").read_text(encoding="utf-8")
assert int(gradle.split("versionCode ",1)[1].split()[0]) >= 267
print("PASS: target name scales and existing target selection is preserved")
