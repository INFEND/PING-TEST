import pathlib
import unittest

SOURCE = pathlib.Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java"


class PingClosedPipeCleanupTest(unittest.TestCase):
    def test_exited_process_close_is_guarded(self):
        src = SOURCE.read_text(encoding="utf-8")
        exited = src.split("else{\n                // Process has exited;", 1)[1].split("String output;", 1)[0]
        self.assertIn("if(reader.isAlive())", exited)
        self.assertIn("try{input.close();}catch(IOException ignored){}", exited)
        self.assertNotIn("process.getInputStream().close();", exited)

    def test_output_still_parsed_after_cleanup(self):
        src = SOURCE.read_text(encoding="utf-8")
        self.assertIn("synchronized(buffer){output=new String(buffer.toByteArray(),StandardCharsets.UTF_8);}", src)
        self.assertIn("exitCode==0?parseIcmpReply(output,probeAddress):null", src)


if __name__ == "__main__":
    unittest.main()
