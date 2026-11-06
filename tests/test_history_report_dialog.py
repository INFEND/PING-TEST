from pathlib import Path
source = Path("app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text()
method = source.split("private void historyDetails(JSONObject obj){", 1)[1].split("private String date(", 1)[0]
assert "new Dialog(this)" in method
assert "eventHeader()" in method
assert "СОХРАНЁННЫЙ ЖУРНАЛ" in method
assert "События этого сеанса не сохранены." in method
assert "new AlertDialog.Builder(this)" not in method
assert "КОПИРОВАТЬ" in method and "ПОДЕЛИТЬСЯ" in method
print("Historical report layout policy: OK")
