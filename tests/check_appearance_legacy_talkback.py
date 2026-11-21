from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
source = (root / "app/src/main/java/com/xarkon/pingtest/QrSettingsCards.java").read_text()
gradle = (root / "app/build.gradle").read_text()
versions = (root / "release_notes/versions.json").read_text()
assert 'Build.VERSION.SDK_INT<30?(selected?", выбрана":", не выбрана"):""' in source
assert 'Build.VERSION.SDK_INT<30?(selected?", выбран":", не выбран"):""' in source
assert source.count('if(Build.VERSION.SDK_INT>=30)tile.setStateDescription(') == 2
assert source.count('info.setClassName(android.widget.Button.class.getName())') == 2
assert "versionCode 251" in gradle and "versionName '1.5.243'" in gradle
assert '"1.5.243": 251' in versions
assert (root / "release_notes/v1.5.243.txt").exists()
print("PASS: Android 8–10 appearance selection accessibility fallback")
