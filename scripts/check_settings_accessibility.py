#!/usr/bin/env python3
"""Static regression guard for collapsible settings accessibility."""
from pathlib import Path
s = Path("app/src/main/java/com/xarkon/pingtest/QrSettingsCards.java").read_text()
assert 'head.setFocusable(true)' in s
assert 'head.setSelected(opened[0])' in s
assert 'head.setSelected(opening)' in s
assert 'head.setStateDescription(opened[0]?"Развёрнуто":"Свёрнуто")' in s
assert 'head.setStateDescription(opening?"Развёрнуто":"Свёрнуто")' in s
assert s.count('if(Build.VERSION.SDK_INT>=30)head.setStateDescription(') == 2
assert 'head.setContentDescription(title+". "+detail+". "+(opening?"Свернуть":"Развернуть"))' in s
print("Settings accessibility static regression: OK")
assert 'titles.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO_HIDE_DESCENDANTS)' in s
assert 'chevron.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO)' in s
assert 'head.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_YES)' in s
assert 'head.setContentDescription(title+". "+detail+". "+(opened?' in s
