from pathlib import Path
root = Path(__file__).resolve().parents[1]
src = (root / 'app/src/main/java/com/xarkon/pingtest/QrSettingsCards.java').read_text(encoding='utf-8')
section = src.split('public static void updates(Activity a,LinearLayout p,Runnable check){', 1)[1].split('SharedPreferences prefs=', 1)[0]
assert 'buttonGlyph.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);' in section
assert 'button.setFocusable(true);' in section
assert 'button.setContentDescription("Проверить обновление");' in section
assert 'title.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);' in section
assert 'info.setClassName(android.widget.Button.class.getName());' in section
assert 'button.setOnClickListener(v->{feedback(a,v);check.run();});' in section
gradle = (root / 'app/build.gradle').read_text(encoding='utf-8')
assert 'versionCode 253' in gradle and "versionName '1.5.245'" in gradle
assert '"1.5.245": 253' in (root / 'release_notes/versions.json').read_text(encoding='utf-8')
assert (root / 'release_notes/v1.5.245.txt').exists()
print('PASS: update-check button accessibility semantics')
