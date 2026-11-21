from pathlib import Path

source = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/QrSettingsCards.java").read_text(encoding="utf-8")
assert source.count('tile.setClickable(true);') >= 2
assert source.count('tile.setAccessibilityDelegate(new View.AccessibilityDelegate()') >= 2
assert source.count('tile.getChildAt(child).setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);') >= 2
assert 'tile.setStateDescription(selected?"Выбрана":"Не выбрана")' in source
assert 'tile.setStateDescription(selected?"Выбран":"Не выбран")' in source
print("Appearance tile accessibility checks passed")
