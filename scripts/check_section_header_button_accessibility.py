#!/usr/bin/env python3
"""Static UI regression guard for collapsible settings headers."""
from pathlib import Path

source = Path("app/src/main/java/com/xarkon/pingtest/QrSettingsCards.java").read_text(encoding="utf-8")
start = source.index("public static void section(")
end = source.index("private static void toggle(", start)
section = source[start:end]
assert "head.setClickable(true);head.setFocusable(true);" in section
assert "head.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_YES);" in section
assert "head.setAccessibilityDelegate(new View.AccessibilityDelegate()" in section
assert "info.setClassName(android.widget.Button.class.getName());" in section
assert 'head.setContentDescription(title+' in section
assert "head.setStateDescription(" in section
assert "sectionGlyph.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);" in section
assert "chevron.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);" in section
print("OK: collapsible settings header has a single accessible button role")
