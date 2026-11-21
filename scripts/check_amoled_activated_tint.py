#!/usr/bin/env python3
"""Regression: activated controls use the AMOLED accent in both themes."""
from pathlib import Path
from xml.etree import ElementTree as ET

styles = {
    style.attrib["name"]: {
        item.attrib["name"]: (item.text or "").strip()
        for item in style.findall("item")
    }
    for style in ET.parse(Path("app/src/main/res/values/styles.xml")).getroot().findall("style")
}
for name in ("Theme.PingTest", "Theme.PingTest.Dialog"):
    theme = styles[name]
    assert theme["android:colorAccent"] == "#55DFCB", name
    assert theme["android:colorControlActivated"] == theme["android:colorAccent"], name
assert styles["Theme.PingTest.Dialog"]["android:colorControlHighlight"] == styles["Theme.PingTest"]["android:colorControlHighlight"]
print("AMOLED activated control tint regression: OK")
