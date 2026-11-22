#!/usr/bin/env python3
"""UI regression: compact metric captions can wrap at large system font sizes."""
from pathlib import Path
source = Path("app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
start = source.index("private void miniMetric(")
end = source.index("private TextView detailStat(", start)
metric = source[start:end]
assert "caption.setMaxLines(2)" in metric
assert "caption.setEllipsize(TextUtils.TruncateAt.END)" in metric
assert "caption.setSingleLine(true)" not in metric
assert "value.setSingleLine(true)" in metric
assert "value.setFontFeatureSettings(\"tnum\")" in metric
assert "parent.addView(col,new LinearLayout.LayoutParams(0,-2,1))" in metric
print("PASS: compact metric labels wrap up to two lines without changing measured values")
