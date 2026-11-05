import pathlib
import unittest

SOURCE=(pathlib.Path(__file__).resolve().parents[1]/'app/src/main/java/com/xarkon/pingtest/PingService.java').read_text(encoding='utf-8')

class UidScopedDnsTests(unittest.TestCase):
    def test_active_network_is_used_for_dns(self):
        self.assertIn('connectivity.getActiveNetwork()', SOURCE)
        self.assertIn('activeNetwork.getAllByName(chosen)', SOURCE)
    def test_no_arbitrary_network_selection(self):
        self.assertNotIn('getAllNetworks()', SOURCE.replace('// Do not resolve via an unrelated network returned by getAllNetworks().',''))
    def test_dns_failure_does_not_fall_back_to_wrong_network(self):
        self.assertIn('activeNetwork==null', SOURCE)
        self.assertNotIn('catch(UnknownHostException', SOURCE)

if __name__=='__main__': unittest.main()
