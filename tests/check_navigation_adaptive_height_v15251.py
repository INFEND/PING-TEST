"""UI regression: bottom navigation grows for large accessibility font scales."""
from pathlib import Path

src = Path("app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
nav = src.split("private void navigation(){", 1)[1].split("private TextView label(", 1)[0]
assert 'String[] names={"Монитор","История","Настройки"}' in nav
assert "cell.setMinimumHeight(Ui.dp(51))" in nav
assert "nav.addView(cell,new LinearLayout.LayoutParams(0,-2,1))" in nav
assert "nav.addView(cell,new LinearLayout.LayoutParams(0,Ui.dp(51),1))" not in nav
assert "cell.setContentDescription(names[i])" in nav
assert "cell.setOnClickListener(v->{if(index!=tab)showTab(index);})" in nav
print("Adaptive bottom navigation UI checks passed")
