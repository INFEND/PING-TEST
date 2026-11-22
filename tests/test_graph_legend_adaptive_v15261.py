#!/usr/bin/env python3
"""UI regression: graph legend stays readable with large fonts."""
from pathlib import Path
s = Path("app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
page = s.split("private void pingPage(){",1)[1].split("private void miniMetric(",1)[0]
assert '● Отлично   ● Норма   ● Плохо' in page
assert 'legend.setMaxLines(2)' in page
assert 'legend.setBreakStrategy(android.text.Layout.BREAK_STRATEGY_HIGH_QUALITY)' in page
assert 'legend.setContentDescription("Качество задержки: отлично, норма, плохо")' in page
assert 'new ForegroundColorSpan(QualityColors.GREEN)' in page
assert 'new ForegroundColorSpan(QualityColors.YELLOW)' in page
assert 'new ForegroundColorSpan(QualityColors.RED)' in page
assert 'graph=new GraphView(this)' in page
assert "versionCode 269" in Path("app/build.gradle").read_text(encoding="utf-8")
print("PASS: graph legend wraps, keeps colors and accessibility")
