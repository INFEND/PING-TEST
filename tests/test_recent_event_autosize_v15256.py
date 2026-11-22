#!/usr/bin/env python3
"""UI regression: recent event RTT remains readable and accessible on narrow displays."""
from pathlib import Path
source = Path("app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
row = source.split("private View eventRow(PingService.ProbeEvent e){", 1)[1].split("private void renderRecentEvents(", 1)[0]
assert "response.setAutoSizeTextTypeUniformWithConfiguration(9,answered?13:11,1," in row
assert "android.util.TypedValue.COMPLEX_UNIT_SP" in row
assert "response.setContentDescription(middle)" in row
assert "response.setEllipsize(TextUtils.TruncateAt.END)" not in row
assert 'response.setFontFeatureSettings("tnum")' in row
assert 'String.format(Locale.US,"%.1f мс",e.latencyMs)' in row
assert "e.payloadBytes" in row
print("PASS: recent event reading auto-sizes without changing measurement formatting")
