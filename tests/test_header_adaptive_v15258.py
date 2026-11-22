#!/usr/bin/env python3
"""Regression: header labels remain single-line and scale on narrow screens."""
from pathlib import Path
s=Path("app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
h=s.split("private void header(){",1)[1].split("private void refreshStatus()",1)[0]
for name, low, high in [("a",13,19),("b",8,10),("status",8,10)]:
    assert f"{name}.setSingleLine(true)" in h
    assert f"{name}.setAutoSizeTextTypeUniformWithConfiguration({low},{high},1,android.util.TypedValue.COMPLEX_UNIT_SP)" in h
assert 'status.setText(running?"● РАБОТАЕТ":!s.error.isEmpty()?"● ОШИБКА":"● ГОТОВ")' in s
assert "versionCode 266" in Path("app/build.gradle").read_text()
print("PASS: adaptive header labels and unchanged status semantics")
