from pathlib import Path

src = (Path(__file__).resolve().parents[1] / 'app/src/main/java/com/xarkon/pingtest/QrSettingsCards.java').read_text(encoding='utf-8')
info = src.split('private static void info(Activity a,LinearLayout p,', 1)[1]
assert 'decorativeGlyph.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);' in info
assert 'row.addView(decorativeGlyph,' in info
assert 'labels.addView(text(a,title,' in info
assert 'labels.addView(text(a,detail,' in info
print('About decorative icon accessibility regression: OK')
