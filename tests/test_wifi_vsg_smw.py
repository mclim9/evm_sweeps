import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add src directory to path for imports
TEST_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(TEST_DIR, '..', 'src'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from driver.wifi_vsg_smw import VSG_driver

class TestWiFiVSG_SMW(unittest.TestCase):
    def setUp(self):
        # Patch BenchConfig to avoid real socket connections during tests
        self.bench_patcher = patch('driver.wifi_vsg_smw.BenchConfig')
        self.mock_bench_class = self.bench_patcher.start()

        # Mock the VSG instrument and its internal socket
        self.mock_vsg = MagicMock()
        self.mock_vsg.s = MagicMock() # Mock the internal socket object

        self.mock_bench_instance = self.mock_bench_class.return_value
        self.mock_bench_instance.VSG_start.return_value = self.mock_vsg

        # Instantiate the driver under test
        self.driver = VSG_driver()

    def tearDown(self):
        self.bench_patcher.stop()

    def test_init_sets_up_vsg(self):
        """Test that __init__ starts VSG connection."""
        self.mock_bench_instance.VSG_start.assert_called_once()
        self.assertEqual(self.driver.VSG, self.mock_vsg)

    def test_vsg_configure_sends_scpi(self):
        """Test vsg_configure sends the correct sequence of SCPI commands."""
        _, elapsed = self.driver.vsg_configure() # method_timer returns (result, time)

        # Check a few key commands
        self.mock_vsg.write.assert_any_call(':SOUR1:BB:WLNN:BW BW320')
        self.mock_vsg.write.assert_any_call(':SOUR1:BB:WLNN:FBL1:TMOD EHT320')
        self.mock_vsg.write.assert_any_call(':SOUR1:BB:WLNN:STAT 1')
        self.mock_vsg.write.assert_any_call(':OUTP1:STAT 1')
        self.mock_vsg.query.assert_any_call(':SOUR1:CORR:OPT:EVM 1;*OPC?')
        self.mock_vsg.write.assert_any_call("SOUR:GPRF:GEN1:ARB:FILE ''")

        self.assertIsInstance(elapsed, float)

    def test_vsg_set_frequency(self):
        """Test vsg_set_frequency sends the correct SCPI command."""
        test_freq = 5.8e9
        self.driver.vsg_set_frequency(test_freq)
        self.mock_vsg.write.assert_called_with(f':SOUR1:FREQ:CW {test_freq}')

    def test_vsg_set_power(self):
        """Test vsg_set_power sends the correct SCPI command."""
        test_pwr = 10.0
        self.driver.vsg_set_power(test_pwr)
        self.mock_vsg.write.assert_called_with(f':SOUR1:POW:POW {test_pwr}')

    def test_vsg_get_extra(self):
        """Test vsg_get_extra returns 'none'."""
        self.assertEqual(self.driver.vsg_get_extra(), 'none')

    def test_vsg_save_state(self):
        """Test vsg_save_state queries instrument and calls os.system."""
        # Mock query responses for Wavename construction, matching execution flow
        self.mock_vsg.query.side_effect = [
            "IDN_RESPONSE", # *IDN?
            "BW320",        # BW
            "EHT320",       # PCKT
            "UP",           # Dir
            "MCS13",        # Mod
            "RU4996",       # RUS
            "OK"            # *OPC? for SETT:STOR
        ]
        self.mock_vsg.s.getpeername.return_value = ("192.168.1.51", 5025)

        with patch('driver.wifi_vsg_smw.os.system') as mock_sys:
            self.driver.vsg_save_state()

            expected_wavename = 'WiFiBW320_EHT320_UP_RU4996_MCS13'
            self.assertEqual(self.driver.Wavename, expected_wavename)
            self.mock_vsg.query.assert_any_call(f':SOUR1:BB:WLNN:SETT:STOR "/var/user/{expected_wavename}";*OPC?')
            mock_sys.assert_called_once_with(r'start \\192.168.1.51\user')

if __name__ == '__main__':
    unittest.main()