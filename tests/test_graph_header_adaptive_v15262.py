from pathlib import Path

source = Path("app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
assert 'TextView graphTitle=label("ГРАФИК ЗАДЕРЖКИ");' in source
assert 'graphTitle.setSingleLine(true);' in source
assert 'graphTitle.setAutoSizeTextTypeUniformWithConfiguration(9,12,1' in source
assert 'TextView graphCount=Ui.text(this,AppPrefs.number(this,"graph_points",150)+" ПАКЕТОВ",10,Ui.muted(),false);' in source
assert 'graphCount.setAutoSizeTextTypeUniformWithConfiguration(9,10,1' in source
assert 'graphHead.addView(graphTitle,new LinearLayout.LayoutParams(0,-2,1));' in source
assert 'graphHead.addView(graphCount);chartCard.addView(graphHead);' in source
print("Graph header UI regression passed")
