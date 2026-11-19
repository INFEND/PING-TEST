"""Exercise the actual route observer methods with minimal Android type stubs."""
from pathlib import Path
import subprocess
import tempfile
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class RouteObserverBehavior(unittest.TestCase):
    def test_transitions(self):
        start = SOURCE.index("    private void observeDefaultNetwork(")
        end = SOURCE.index("    private void startRouteMonitor()", start)
        java = """
import java.util.Objects;
import java.util.HashSet;
import java.util.List;
public class RouteHarness {
    static class Network {}
    static class LinkProperties {
        String iface;
        LinkProperties(String iface){this.iface=iface;}
        String getInterfaceName(){return iface;}
        List<String> getLinkAddresses(){return List.of();}
        List<String> getRoutes(){return List.of();}
    }
    static class ConnectivityManager {
        static class NetworkCallback {}
        LinkProperties properties;
        LinkProperties getLinkProperties(Network network){return properties;}
    }
    static class NetworkCapabilities {
        static final int TRANSPORT_VPN=4;
        boolean vpn, contradictory;
        NetworkCapabilities(boolean vpn){this.vpn=vpn;}
        boolean hasTransport(int transport){return vpn;}
    }
    static class VpnGuard {
        enum Route { VPN, DIRECT, UNKNOWN }
        static Route classify(NetworkCapabilities caps){
            return caps.contradictory?Route.UNKNOWN:caps.vpn?Route.VPN:Route.DIRECT;
        }
    }
    static final Object LOCK=new Object();
    ConnectivityManager.NetworkCallback routeCallback;
    Network observedNetwork;
    VpnGuard.Route observedRoute;
    Boolean observedBlocked;
    IcmpPath observedLink;
    long routeGeneration;
""" + SOURCE[start:end] + """
    void expect(long expected){
        if(routeGeneration!=expected)throw new AssertionError(routeGeneration+" != "+expected);
    }
    public static void main(String[] args){
        RouteHarness h=new RouteHarness();
        ConnectivityManager cm=new ConnectivityManager();
        Network probe=new Network();
        if(readIcmpPath(cm,probe)!=null)throw new AssertionError("missing properties");
        cm.properties=new LinkProperties("wlan0");
        IcmpPath before=readIcmpPath(cm,probe);
        cm.properties.iface="tun0";
        if(sameIcmpPath(before,readIcmpPath(cm,probe)))throw new AssertionError("mutable path snapshot");
        if(readIcmpPath(null,probe)!=null||readIcmpPath(cm,null)!=null)throw new AssertionError("missing network");
        Network a=new Network(), b=new Network();
        ConnectivityManager.NetworkCallback c=new ConnectivityManager.NetworkCallback();
        ConnectivityManager.NetworkCallback stale=new ConnectivityManager.NetworkCallback();
        h.routeCallback=c;
        h.observeDefaultNetwork(c,a,false); h.expect(1);
        h.observeDefaultBlocked(c,a,false); h.expect(1);
        h.observeDefaultBlocked(stale,a,true); h.expect(1);
        h.observeDefaultBlocked(c,b,true); h.expect(1);
        h.observeDefaultBlocked(c,a,true); h.expect(2);
        h.observeDefaultBlocked(c,a,true); h.expect(2);
        h.observeDefaultBlocked(c,a,false); h.expect(3);
        h.observeDefaultCapabilities(c,a,new NetworkCapabilities(false)); h.expect(3);
        h.observeDefaultCapabilities(c,a,new NetworkCapabilities(true)); h.expect(4);
        NetworkCapabilities ambiguous=new NetworkCapabilities(true);
        ambiguous.contradictory=true;
        h.observeDefaultCapabilities(c,a,ambiguous); h.expect(5);
        h.observeDefaultCapabilities(c,a,ambiguous); h.expect(5);
        h.observeDefaultCapabilities(c,a,new NetworkCapabilities(true)); h.expect(6);
        h.observeDefaultNetwork(c,b,false); h.expect(7);
        h.observeDefaultNetwork(c,a,true); h.expect(7);
        h.observeDefaultBlocked(c,b,true); h.expect(8);
        h.observeDefaultBlocked(c,b,false); h.expect(9);
        LinkProperties link=new LinkProperties("wlan0");
        h.observeDefaultLink(c,b,link); h.expect(9);
        h.observeDefaultLink(c,b,new LinkProperties("wlan0")); h.expect(9);
        h.observeDefaultLink(stale,b,new LinkProperties("tun0")); h.expect(9);
        h.observeDefaultLink(c,a,new LinkProperties("tun0")); h.expect(9);
        link.iface="tun0";
        h.observeDefaultLink(c,b,link); h.expect(10);
        h.observeDefaultLink(c,b,link); h.expect(10);
        h.observeDefaultNetwork(c,a,false); h.expect(11);
        h.observeDefaultLink(c,a,new LinkProperties("wlan0")); h.expect(11);
        h.routeCallback=null;
        h.observeDefaultBlocked(c,a,true); h.expect(11);
        h.observeDefaultLink(c,a,new LinkProperties("tun0")); h.expect(11);
    }
}
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "RouteHarness.java"
            path.write_text(java, encoding="utf-8")
            subprocess.run(["javac", "-encoding", "UTF-8", str(path)], check=True, timeout=60)
            subprocess.run(["java", "-cp", tmp, "RouteHarness"], check=True, timeout=30)

if __name__ == "__main__":
    unittest.main()
