import pathlib
import subprocess
import tempfile
import unittest

SOURCE = (pathlib.Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text()

class RouteLinkTest(unittest.TestCase):
    def test_path_comparison(self):
        start = SOURCE.index("    private static final class IcmpPath")
        end = SOURCE.index("    private void observeDefaultLink(", start)
        code = """
import java.util.*;
class Harness {
    static class LinkProperties {
        String iface; List<String> addresses, routes;
        LinkProperties(String i, List<String> a, List<String> r){iface=i;addresses=a;routes=r;}
        String getInterfaceName(){return iface;}
        List<String> getLinkAddresses(){return addresses;}
        List<String> getRoutes(){return routes;}
    }
""" + SOURCE[start:end] + """
    public static void main(String[] args) {
        LinkProperties a=new LinkProperties("wlan0",List.of("a","b"),List.of("r","s"));
        if(!sameIcmpPath(new IcmpPath(a),new IcmpPath(new LinkProperties("wlan0",List.of("b","a"),List.of("s","r")))))throw new AssertionError("ordering");
        if(sameIcmpPath(new IcmpPath(a),new IcmpPath(new LinkProperties("tun0",a.addresses,a.routes))))throw new AssertionError("interface");
        if(sameIcmpPath(new IcmpPath(a),new IcmpPath(new LinkProperties("wlan0",List.of("c"),a.routes))))throw new AssertionError("address");
        if(sameIcmpPath(new IcmpPath(a),new IcmpPath(new LinkProperties("wlan0",a.addresses,List.of("t")))))throw new AssertionError("route");
    }
}
"""
        with tempfile.TemporaryDirectory() as tmp:
            p=pathlib.Path(tmp)/"Harness.java"
            p.write_text(code)
            subprocess.run(["javac",str(p)],check=True)
            subprocess.run(["java","-cp",tmp,"Harness"],check=True)

    def test_public_sdk_snapshot(self):
        self.assertNotIn("new LinkProperties(", SOURCE)
        self.assertIn("observedLink=new IcmpPath(link)", SOURCE)

    def test_callback_wiring(self):
        self.assertIn("observeDefaultLink(this,network,properties)", SOURCE)
        self.assertIn("!sameIcmpPath(observedLink,next))routeGeneration++", SOURCE)
        self.assertIn("routeGeneration!=sessionGeneration", SOURCE)
        self.assertIn("observedLink=null;", SOURCE)

if __name__ == "__main__":
    unittest.main()
