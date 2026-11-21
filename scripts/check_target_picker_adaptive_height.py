#!/usr/bin/env python3
"""Static regression guard for the target picker dialog sizing."""
from pathlib import Path

source = Path("app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
start = source.index("ScrollView scroll=new ScrollView(this){", source.index('"Выбор узла"'))
end = source.index("private ImageView icon(", start)
picker = source[start:end]

assert "onMeasure(int widthMeasureSpec,int heightMeasureSpec)" in picker
assert "View.MeasureSpec.AT_MOST" in picker
assert "Math.min(maxHeight,View.MeasureSpec.getSize(heightMeasureSpec))" in picker
assert "scroll.setFillViewport(false);scroll.addView(body)" in picker
assert "WindowManager.LayoutParams.WRAP_CONTENT" in picker
assert "window.setLayout(" in picker
assert "heightPixels*.83f));" not in picker
assert "row.setOnClickListener" in source
print("PASS: target picker adapts to content, with bounded scrolling")
