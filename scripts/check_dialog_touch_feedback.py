#!/usr/bin/env python3
"""Regression: AMOLED dialog touch feedback matches the main theme."""
from pathlib import Path
from xml.etree import ElementTree as ET

root = ET.parse(Path("app/src/main/res/values/styles.xml")).getroot()
styles = {
    s.attrib["name"]: {i.attrib["name"]: (i.text or "").strip() for i in s.findall("item")}
    for s in root.findall("style")
}
main = styles["Theme.PingTest"]
dialog = styles["Theme.PingTest.Dialog"]
assert main["android:colorControlHighlight"] == "#3355DFCB"
assert dialog["android:colorControlHighlight"] == main["android:colorControlHighlight"]
assert dialog["android:colorAccent"] == main["android:colorAccent"]
assert dialog["android:windowBackground"] == "#101215"
print("AMOLED dialog press feedback regression: OK")
