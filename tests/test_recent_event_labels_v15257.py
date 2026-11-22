#!/usr/bin/env python3
"""UI regression: recent event number and payload remain complete and accessible."""
from pathlib import Path
source = Path("app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
row = source.split("private View eventRow(PingService.ProbeEvent e){", 1)[1].split("private void renderRecentEvents(", 1)[0]
for name, value in [("number", '"#"+e.number'), ("size", "String.valueOf(e.payloadBytes)")]:
    assert f"{name}.setSingleLine(true)" in row
    assert f"{name}.setAutoSizeTextTypeUniformWithConfiguration(9,12,1," in row
    assert f"{name}.setContentDescription({value})" in row
assert 'String.format(Locale.US,"%.1f мс",e.latencyMs)' in row
assert "e.payloadBytes" in row
gradle = Path("app/build.gradle").read_text(encoding="utf-8")
# Preserve the UI assertion across later application version increments.
assert int(gradle.split("versionCode ", 1)[1].split()[0]) >= 265
assert tuple(map(int, gradle.split("versionName '", 1)[1].split("'", 1)[0].split("."))) >= (1, 5, 257)
print("PASS: event number and payload labels fit and preserve values")
