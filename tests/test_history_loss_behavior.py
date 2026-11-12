"""Execute the actual historical loss calculations in a JVM."""
from pathlib import Path
import subprocess
import tempfile
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          "app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")

class HistoryLossBehavior(unittest.TestCase):
    def test_card_and_report_agree(self):
        start = SOURCE.index('int sent=o.optInt("sent");int lost=o.optInt("lost");')
        end = SOURCE.index("double percent=", start)
        card = SOURCE[start:end]
        start = SOURCE.index('int sent=obj.optInt("sent"),ok=obj.optInt("ok");')
        end = SOURCE.index('String method=', start)
        report = SOURCE[start:end]
        java = """
import java.util.*;
public class HistoryHarness {
    static class Record {
        Map<String,Integer> fields = new HashMap<>();
        Record(int sent, int ok, Integer done, Integer lost) {
            fields.put("sent",sent); fields.put("ok",ok);
            if(done!=null) fields.put("done",done);
            if(lost!=null) fields.put("lost",lost);
        }
        int optInt(String key) { return fields.getOrDefault(key,0); }
        boolean has(String key) { return fields.containsKey(key); }
    }
    static int[] card(Record o) {
""" + card + """
        return new int[]{completed,lost};
    }
    static int[] report(Record obj) {
""" + report + """
        return new int[]{completed,lost};
    }
    static void check(Record r, int completed, int lost) {
        int[] expected = {completed,lost};
        if(!Arrays.equals(expected,card(r)) || !Arrays.equals(expected,report(r)))
            throw new AssertionError(r.fields.toString());
    }
    public static void main(String[] args) {
        check(new Record(0,0,0,0),0,0);
        check(new Record(5,0,5,0),0,0);
        check(new Record(10,5,9,2),7,2);
        check(new Record(10,0,5,5),5,5);
        check(new Record(10,5,8,null),8,3);
        check(new Record(10,5,null,null),10,5);
        check(new Record(10,10,10,0),10,0);
        check(new Record(1,0,1,-1),0,0);
    }
}
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "HistoryHarness.java"
            path.write_text(java, encoding="utf-8")
            subprocess.run(["javac", "-encoding", "UTF-8", str(path)], check=True, timeout=60)
            subprocess.run(["java", "-cp", tmp, "HistoryHarness"], check=True, timeout=30)

if __name__ == "__main__":
    unittest.main()
