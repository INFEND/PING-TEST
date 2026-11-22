#!/usr/bin/env python3
"""Static UI regression guard for live journal window bounds and scroll behavior."""
from pathlib import Path
s = Path("app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
start = s.index('journalDialog=dialog;')
end = s.index('private void stopJournalScrollAnimation()', start)
journal = s[start:end]
assert "getWindowVisibleDisplayFrame(visible)" in journal
assert "visible.height()>0?visible.height()" in journal
assert "Math.min((int)(availableHeight*.85f),Ui.dp(640))" in journal
assert "heightPixels*.77f" not in journal
assert "frame.addView(scroll,new LinearLayout.LayoutParams(-1,0,1))" in journal
assert "return false; // Never interfere with normal manual scrolling/fling." in journal
assert "journalFollowTail=true" in journal
assert 'copy.setOnClickListener' in journal and 'close.setOnClickListener' in journal
print("PASS: journal bounded to visible height with scrolling and actions preserved")
