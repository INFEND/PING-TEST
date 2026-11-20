#!/usr/bin/env python3
"""Guard navigation tab semantics without touching ping logic."""
from pathlib import Path
s = Path("app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text()
start = s.index("private void navigation()")
end = s.index("private TextView label(", start)
nav = s[start:end]
for expected in (
    "cell.setFocusable(true)",
    "cell.setContentDescription(names[i])",
    "cell.setSelected(selected)",
    "cell.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_YES)",
    "glyph.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO)",
    "label.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO)",
    "cell.setOnClickListener(v->{if(index!=tab)showTab(index);})",
):
    assert expected in nav, expected
assert 'String[] names={"Монитор","История","Настройки"}' in nav
assert 'Ui.dp(51)' in nav
print("Navigation accessibility UI regression: OK")
