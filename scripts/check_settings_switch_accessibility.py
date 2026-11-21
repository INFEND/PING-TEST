#!/usr/bin/env python3
"""Regression guard for accessible settings switches, no measurement changes."""
from pathlib import Path

source = Path("app/src/main/java/com/xarkon/pingtest/QrSettingsCards.java").read_text(encoding="utf-8")
start = source.index("private static void toggle(")
end = source.index("public static void appearance(", start)
toggle = source[start:end]
for expected in (
    "decoration.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO)",
    "labels.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO_HIDE_DESCENDANTS)",
    "line.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO)",
    'sw.setContentDescription(title+". "+detail)',
    "sw.setOnCheckedChangeListener((b,on)->action.accept(on))",
    "sw.setChecked(!sw.isChecked())",
):
    assert expected in toggle, f"Missing settings accessibility contract: {expected}"
print("Settings switch accessibility regression: OK")
