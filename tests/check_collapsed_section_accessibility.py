from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/QrSettingsCards.java"
code = SRC.read_text(encoding="utf-8")
assert "body.setImportantForAccessibility(opened[0]?View.IMPORTANT_FOR_ACCESSIBILITY_AUTO:View.IMPORTANT_FOR_ACCESSIBILITY_NO_HIDE_DESCENDANTS);" in code
assert "body.setImportantForAccessibility(opening?View.IMPORTANT_FOR_ACCESSIBILITY_AUTO:View.IMPORTANT_FOR_ACCESSIBILITY_NO_HIDE_DESCENDANTS);" in code
assert code.index("body.setImportantForAccessibility(opening?") < code.index("final int id=++revision[0];")
print("Collapsed settings accessibility regression: OK")
