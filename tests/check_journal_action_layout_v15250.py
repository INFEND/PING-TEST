"""UI regression: journal actions must remain readable at narrow widths/large fonts."""
from pathlib import Path

src = Path("app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
start = src.index('TextView heading=Ui.text(this,"Живой журнал"')
end = src.index("private void stopJournalScrollAnimation()", start)
journal = src[start:end]
assert "screenWidthDp<360" in journal
assert "fontScale>1.25f" in journal
assert "stackJournalActions?Ui.vertical(this):Ui.horizontal(this)" in journal
assert "actions.addView(copy,new LinearLayout.LayoutParams(-1,Ui.dp(48)))" in journal
assert 'actions.addView(close,Ui.margins(-1,48,8,0))' in journal
assert "actions.addView(copy,new LinearLayout.LayoutParams(0,Ui.dp(44),1))" in journal
assert 'copy.setOnClickListener(v->copy(String.join("\\n",PingService.snapshot().log)))' in journal
assert "close.setOnClickListener(v->dialog.dismiss())" in journal
assert "frame.addView(scroll,new LinearLayout.LayoutParams(-1,0,1))" in journal
print("Journal action layout regression checks passed")
