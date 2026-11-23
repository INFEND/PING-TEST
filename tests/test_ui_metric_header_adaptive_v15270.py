"""UI regression: long quality labels and detail metrics remain adaptive."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
GRADLE = (ROOT / "app/build.gradle").read_text(encoding="utf-8")

def test_quality_header_adapts():
    assert "qualityState.setSingleLine(true);" in MAIN
    assert "qualityState.setAutoSizeTextTypeUniformWithConfiguration(8,10,1" in MAIN
    assert "qualityState.setMaxWidth(Ui.dp(122));" in MAIN

def test_detail_metrics_adapt():
    assert "value.setSingleLine(true);" in MAIN
    assert "value.setAutoSizeTextTypeUniformWithConfiguration(10,15,1" in MAIN
    assert 'bestText.setText(s.timed==0?"—":fmt(s.min)+" мс");' in MAIN
    assert 'maxText.setText(s.timed==0?"—":fmt(s.max)+" мс");' in MAIN

def test_release_version():
    assert "versionCode 278" in GRADLE
    assert "versionName '1.5.270'" in GRADLE
