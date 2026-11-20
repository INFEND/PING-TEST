#!/usr/bin/env python3
"""Regression: translucent AMOLED press feedback, without altering theme palette."""
from pathlib import Path
from xml.etree import ElementTree as ET
root = ET.parse(Path('app/src/main/res/values/styles.xml')).getroot()
styles = {s.attrib['name']: {i.attrib['name']: (i.text or '').strip() for i in s.findall('item')} for s in root.findall('style')}
for name in ('Theme.PingTest', 'Theme.PingTest.Dialog'):
    items = styles[name]
    assert items['android:colorAccent'] == '#55DFCB'
    assert items['android:colorControlHighlight'] == '#3355DFCB'
    assert int(items['android:colorControlHighlight'][1:3],16) < 128
assert styles['Theme.PingTest']['android:windowBackground'] == '#000000'
assert styles['Theme.PingTest.Dialog']['android:windowBackground'] == '#101215'
print('AMOLED touch feedback regression: OK')
