from pathlib import Path

root = Path(__file__).resolve().parents[1]
src = (root / 'app/src/main/java/com/xarkon/pingtest/QrSettingsCards.java').read_text()
gradle = (root / 'app/build.gradle').read_text()
versions = (root / 'release_notes/versions.json').read_text()
assert 'UiIcon sectionGlyph=symbol(a,glyph,29,AppPrefs.accent(a));' in src
assert 'sectionGlyph.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);' in src
assert 'head.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_YES);' in src
assert 'head.setContentDescription(title+". "+detail+' in src
assert "versionCode 252" in gradle and "versionName '1.5.244'" in gradle
assert '"1.5.244": 252' in versions
assert (root / 'release_notes/v1.5.244.txt').exists()
print('PASS: settings section decorative glyph is excluded from TalkBack navigation')
