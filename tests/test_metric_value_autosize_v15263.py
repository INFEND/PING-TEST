from pathlib import Path

root = Path(__file__).resolve().parents[1]
src = (root / "app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text()
gradle = (root / "app/build.gradle").read_text()
versions = (root / "release_notes/versions.json").read_text()
start = src.index("private void miniMetric(")
end = src.index("private TextView detailStat(", start)
block = src[start:end]
assert "value.setSingleLine(true);" in block
assert "value.setAutoSizeTextTypeUniformWithConfiguration(10,22,1,android.util.TypedValue.COMPLEX_UNIT_SP);" in block
assert "value.setFontFeatureSettings(\"tnum\");" in block
import re
match = re.search(r"versionCode\s+(\d+)", gradle)
assert match is not None and int(match.group(1)) >= 271
assert re.search(r"versionName\s+[\'\"]1\.5\.\d+[\'\"]", gradle)
assert '"1.5.263": 271' in versions
print("UI metric autosize regression OK")
