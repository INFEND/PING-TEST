from pathlib import Path
root=Path(__file__).resolve().parents[1]
main=(root/"app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text()
store=(root/"app/src/main/java/com/xarkon/pingtest/HistoryStore.java").read_text()
ota=(root/"app/src/main/java/com/xarkon/pingtest/OtaProgressDialog.java").read_text()
icons=(root/"app/src/main/java/com/xarkon/pingtest/UiIcon.java").read_text()
assert "slider.setMax(19)" in main and "50+progress*50" in main
assert "HistoryStore.setLimit(MainActivity.this,selected)" in main
assert "updated.length() < limit(c)" in store and "trimmed.length()<safe" in store
assert 'detailStat(detail,"МИН")' in main
assert 'detailStat(detail,"СРЕД")' in main
assert 'detailStat(detail,"МАКС")' in main
assert "jitterText" not in main
assert "panel=Ui.surface(a)" in ota and "notesScroll.setBackground(shape(Ui.bg(a)" in ota
assert "Path crescent" in icons and 'case "amoled":rect' in icons
print("PASS: history limit, metrics, theme-aware OTA and icons")
