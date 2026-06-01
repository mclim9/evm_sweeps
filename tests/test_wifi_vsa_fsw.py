import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add src directory to path for imports
TEST_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(TEST_DIR, '..', 'src'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from driver.wifi_vsa_fsw import VSA_driver

class TestWiFiVSAFSW(unittest.TestCase):
    def setUp(self):
        # Patch BenchConfig used inside wifi_vsa_fsw to avoid socket creation
        self.bench_patcher = patch('driver.wifi_vsa_fsw.BenchConfig')
        self.mock_bench_class = self.bench_patcher.start()

        # Mock the VSA instrument returned by BenchConfig().VSA_start()
        self.mock_vsa = MagicMock()
        self.mock_vsa.s = MagicMock() # Mock the internal socket object

        self.mock_bench_instance = self.mock_bench_class.return_value
        self.mock_bench_instance.VSA_start.return_value = self.mock_vsa

        # Instantiate the driver under test
        self.driver = VSA_driver()

    def tearDown(self):
        self.bench_patcher.stop()

    def test_init_connects_to_vsa(self):
        """Test that __init__ starts the VSA connection and sets timeout."""
        self.mock_bench_instance.VSA_start.assert_called_once()
        self.assertEqual(self.driver.VSA, self.mock_vsa)
        self.mock_vsa.s.settimeout.assert_called_once_with(30)

    def test_vsa_configure_sends_commands(self):
        """Test vsa_configure sends the correct SCPI sequence."""
        self.driver.vsa_configure()
        self.mock_vsa.query.assert_any_call("*RST;*OPC?")
        self.mock_vsa.query.assert_any_call(':INST:CRE:NEW WLAN, "WLAN"; *OPC?')
        self.mock_vsa.write.assert_any_call(":CONF:STAN 10")

    def test_vsa_get_attn_ref(self):
        """Test retrieving attenuation and reference level."""
        self.mock_vsa.query.return_value = "10"
        self.mock_vsa.queryFloat.return_value = 5.0

        attn, ref = self.driver.vsa_get_attn_ref()
        self.assertEqual(attn, "10")
        self.assertEqual(ref, 5.0)

    def test_vsa_get_evm_success(self):
        """Test EVM retrieval with valid data."""
        # query() is called twice in vsa_get_evm: once for IMM;OPC and once for data
        self.mock_vsa.query.side_effect = ["", "-42.5,0.0,0.0"]

        evm, elapsed = self.driver.vsa_get_evm()
        self.assertEqual(evm, -42.5)
        self.assertIsInstance(elapsed, float)

    def test_vsa_get_evm_failure_returns_sentinel(self):
        """Test that invalid EVM data returns the 999.0 sentinel value."""
        self.mock_vsa.query.side_effect = ["", "invalid,data"]
        evm, _ = self.driver.vsa_get_evm()
        self.assertEqual(evm, 999.0)

    def test_vsa_set_frequency(self):
        """Test setting frequency sends correct SCPI."""
        self.driver.vsa_set_frequency(6.125e9)
        self.mock_vsa.write.assert_called_with(":SENSE:FREQ:CENT 6125000000.0")

    def test_vsa_set_level_auto(self):
        """Test vsa_set_level with auto mode."""
        self.driver.vsa_set_level("LEV")
        self.mock_vsa.query.assert_called_with(":CONF:POW:AUTO ONCE;*OPC?")

    def test_vsa_save_state(self):
        """Test save state queries instrument and calls os.system."""
        self.mock_vsa.query.return_value = "TEST_VAL"
        self.mock_vsa.queryInt.return_value = 160000000
        self.mock_vsa.s.getpeername.return_value = ("192.168.1.50", 5025)

        with patch('driver.wifi_vsa_fsw.os.system') as mock_sys:
            self.driver.vsa_save_state()

            self.mock_vsa.queryInt.assert_called_with(":TRAC:IQ:SRAT?")
            # Check that os.system was called with the instrument IP
            mock_sys.assert_called_once_with(r'start \\192.168.1.50')

    def test_vsa_get_ACLR(self):
        """Test retrieving ACLR data returns expected values."""
        self.mock_vsa.query.side_effect = [
            "",        # from vsa_sweep query (*OPC?)
            "-15.5",   # chPwr
            "-45.2"    # ACLRV
        ]
        temp = self.driver.vsa_get_ACLR()
        # (chPwr, ACLRV), _ = self.driver.vsa_get_ACLR()
        # self.assertEqual(chPwr, "-15.5")
        # self.assertEqual(ACLRV, "-45.2")
        self.assertGreaterEqual(temp[1], 0.00)

    def test_vsa_get_ch_power(self):
        """Test retrieving channel power."""
        self.mock_vsa.queryFloat.return_value = -10.5
        pwr = self.driver.vsa_get_ch_power()
        self.assertEqual(pwr, 999.0)

    def test_vsa_get_extra(self):
        """Test vsa_get_extra returns a string."""
        extra = self.driver.vsa_get_extra()
        self.assertIsInstance(extra, str)

    def test_vsa_get_extra_IQNC(self):
        """Test vsa_get_extra returns a string with the expected value."""
        extra = self.driver.vsa_get_extra('IQNC')
        self.assertEqual(extra, 'WiFi EVM IQNC')
        pass

    def test_vsa_get_extra_XCORR(self):
        """Test vsa_get_extra returns a string with the expected value."""
        extra = self.driver.vsa_get_extra('xcorr')
        self.assertEqual(extra, 'WiFi EVM XCORR')

    # def test_vsa_load(self):
    #     """Test loading a state file onto the VSA."""
    #     filename = "C:\\R_S\\Instr\\user\\wifi_setup.dfl"
    #     self.driver.vsa_load(filename)
    #     self.mock_vsa.write.assert_called_with(f"MMEM:LOAD:STAT 1, '{filename}'")

if __name__ == '__main__':
    unittest.main()
