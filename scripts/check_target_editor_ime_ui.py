#!/usr/bin/env python3
"""Static UI regression guard: target editor remains usable with keyboard visible."""
from pathlib import Path

source = Path('app/src/main/java/com/xarkon/pingtest/MainActivity.java').read_text(encoding='utf-8')
start = source.index('private void editTarget(TargetStore.Target current)')
end = source.index('private void showVpnOnEntry()', start)
editor = source[start:end]
assert 'ScrollView formScroll=new ScrollView(this)' in editor
assert 'formScroll.addView(frame)' in editor
assert '.setView(formScroll)' in editor
assert 'SOFT_INPUT_ADJUST_RESIZE' in editor
assert 'frame.addView(name)' in editor and 'frame.addView(address)' in editor
assert 'name.setError(' in editor and 'address.setError(' in editor
assert 'TargetStore.save(' in editor and 'TargetStore.remove(' in editor
assert 'dialog.dismiss()' in editor
print('PASS: target editor scrolls with IME and preserves validation/actions')
