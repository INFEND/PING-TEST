#!/usr/bin/env python3
"""UI regression: dialog secondary text contrast and unchanged AMOLED palette."""
from pathlib import Path
import re
from xml.etree import ElementTree as ET
p = Path("app/src/main/res/values/styles.xml")
root = ET.parse(p).getroot()
dialog = next(s for s in root.findall("style") if s.get("name") == "Theme.PingTest.Dialog")
items = {i.get("name"): (i.text or "").strip() for i in dialog.findall("item")}
assert items["android:textColorSecondary"] == "#B9C5CD"
assert items["android:windowBackground"] == "#101215"
assert items["android:textColorPrimary"] == "#F5F7F9"
assert items["android:colorAccent"] == "#55DFCB"
def luminance(h):
    rgb = [int(h[i:i+2],16)/255 for i in (1,3,5)]
    linear = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    return sum(a*b for a,b in zip(linear,(.2126,.7152,.0722)))
fg,bg = luminance(items["android:textColorSecondary"]),luminance(items["android:windowBackground"])
assert (max(fg,bg)+.05)/(min(fg,bg)+.05) >= 7.0
print("Dialog AMOLED contrast regression: OK")
