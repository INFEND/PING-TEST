#!/usr/bin/env python3
"""Static regression: scaled system fonts must not be clipped by metric row heights."""
from pathlib import Path
source = Path("app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
assert "big.addView(last,new LinearLayout.LayoutParams(0,-2,1));" in source
assert "last.setMinimumHeight(Ui.dp(64));" in source
assert "value.setMinHeight(Ui.dp(29));" in source
assert "col.addView(value,Ui.margins(-1,-2,0,0));" in source
assert "big.addView(last,new LinearLayout.LayoutParams(0,Ui.dp(64),1));" not in source
assert "col.addView(value,Ui.margins(-1,29,0,0));" not in source
assert "last.update(s.last,false,sameSession)" in source
assert "avg.update(s.avg(),false,sameSession)" in source
assert "failed.update(s.ok+s.lost==0?-1:s.lossPct(),true,sameSession)" in source
print("PASS: live metrics grow vertically with font scaling; data bindings unchanged")
