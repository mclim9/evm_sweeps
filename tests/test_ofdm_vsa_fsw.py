from unittest.mock import MagicMock, patch
import unittest
import sys
import os

# Add src directory to path for imports
TEST_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(TEST_DIR, '..', 'src'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from driver.OFDM_vsa_fsw import VSA_driver

class Test_OFDM_VSA_FSW(unittest.TestCase):
    def setUp(self):
        # Patch BenchConfig to avoid real socket connections during tests
        self.bench_patcher = patch('driver.OFDM_vsa_fsw.BenchConfig')
        self.mock_bench_class = self.bench_patcher.start()

        # Mock the VSA instrument and its internal socket
        self.mock_vsa = MagicMock()
        self.mock_vsa.s = MagicMock()

        self.mock_bench_instance = self.mock_bench_class.return_value
        self.mock_bench_instance.VSA_start.return_value = self.mock_vsa

        # Link queryInt and queryFloat to use the query mock, mimicking iSocket behavior
        self.mock_vsa.queryInt.side_effect = lambda s: int(self.mock_vsa.query(s))
        self.mock_vsa.queryFloat.side_effect = lambda s: float(self.mock_vsa.query(s))

        self.driver = VSA_driver()

    def tearDown(self):
        self.bench_patcher.stop()

    def test_init_sets_up_vsa(self):
        """Test that __init__ starts VSA connection and sets timeout."""
        self.mock_bench_instance.VSA_start.assert_called_once()
        self.assertEqual(self.driver.VSA, self.mock_vsa)
        self.mock_vsa.s.settimeout.assert_called_once_with(30)

    def test_vsa_configure_sends_scpi(self):
        """Test vsa_configure sends the correct sequence of SCPI commands."""
        # vsa_configure is decorated with method_timer, returns (None, time)
        _, elapsed = self.driver.vsa_configure()

        self.mock_vsa.query.assert_any_call('*RST;*OPC?')
        self.mock_vsa.query.assert_any_call(':INST:CRE:NEW OFDM, "OFDM VSA"; *OPC?')

    def test_vsa_get_ACLR(self):
        """Test retrieving ACLR data returns expected values."""

        temp = self.driver.vsa_get_ACLR()
        self.assertGreaterEqual(temp[1], -9999)

    def test_vsa_get_attn_ref(self):
        """Test retrieving attenuation and reference level."""
        self.mock_vsa.query.side_effect = ["10", "11", "12"]
        attn, refl, preamp = self.driver.vsa_get_attn_ref()
        self.assertEqual(attn, "10")
        self.assertEqual(refl, 11.0)
        self.assertEqual(preamp, "12")

    def test_vsa_get_ch_power(self):
        """Test retrieving channel power."""
        self.mock_vsa.query.side_effect = ["curr_app", "3e9", '3', '1', '-10.5', 'App']
        self.mock_vsa.queryFloat.return_value = -10.5
        pwr = self.driver.vsa_get_ch_power()
        self.assertEqual(pwr, -10.5)

    def test_vsa_configure_sends_commands(self):
        """Test vsa_configure sends the correct SCPI sequence."""
        self.driver.vsa_configure()
        self.mock_vsa.query.assert_any_call("*RST;*OPC?")
        self.mock_vsa.query.assert_any_call(':INST:CRE:NEW OFDM, "OFDM VSA"; *OPC?')

    def test_vsa_get_evm_success(self):
        """Test EVM retrieval on a successful sweep."""
        # vsa_sweep is called, which calls query('*OPC?')
        self.mock_vsa.query.side_effect = ["1", "-50.5"]

        evm, _ = self.driver.vsa_get_evm()
        self.assertEqual(evm, -50.5)

    def test_vsa_get_evm_retry(self):
        """Test that EVM retrieval retries once on failure."""
        self.mock_vsa.query.side_effect = ["1", Exception("Comm error"), "1", -50.5]
        evm, _ = self.driver.vsa_get_evm()
        self.assertEqual(evm, -50.5)

    def test_vsa_get_extra(self):
        """Test vsa_get_extra string"""
        extra = self.driver.vsa_get_extra()
        self.assertIsInstance(extra, str)
        self.assertEqual(extra, 'OFDM EVM')

    def test_vsa_get_extra_IQNC(self):
        """Test vsa_get_extra returns a string with the expected value."""
        extra = self.driver.vsa_get_extra('IQNC')
        self.assertEqual(extra, 'OFDM EVM IQNC')

    def test_vsa_get_extra_XCORR(self):
        """Test vsa_get_extra returns a string with the expected value."""
        extra = self.driver.vsa_get_extra('xcorr')
        self.assertEqual(extra, 'OFDM EVM XCORR')

    def test_vsa_get_extra_ACLR_RMS(self):
        """Test vsa_get_extra returns a string with the expected value."""
        extra = self.driver.vsa_get_extra('ACLR_RMS')
        self.assertEqual(extra, 'OFDM EVM ACLR_RMS')

    def test_vsa_get_extra_XCORR_RMS(self):
        """Test vsa_get_extra returns a string with the expected value."""
        extra = self.driver.vsa_get_extra('XCORR_RMS')
        self.assertEqual(extra, 'OFDM EVM XCORR_RMS')

    def test_vsa_get_waveform_info(self):
        """Test construction of OFDM info string."""
        info = self.driver.vsa_get_waveform_info()
        self.assertIn("OFDM", info)
        self.assertEqual(self.driver.Wavename, info)

    def test_vsa_set_frequency(self):
        """Test setting frequency sends correct SCPI."""
        self.driver.vsa_set_frequency(6.125e9)
        self.mock_vsa.write.assert_any_call(":SENSE:FREQ:CENT 6125000000.0")

    def test_vsa_set_level_auto(self):
        """Test vsa_set_level with auto mode."""
        self.driver.vsa_set_level("LEV")
        self.mock_vsa.query.assert_any_call(":SENS:ADJ:LEV;*OPC?")

    def test_vsa_set_level_man(self):
        """Test vsa_set_level with manual mode."""
        self.mock_vsa.query.side_effect = ["1", "chApp", "12.34e5", "4", "5", "-12.3", '1']
        self.driver.vsa_set_level("MAN")
        self.mock_vsa.write.assert_any_call(':INP:ATT:AUTO ON')                         # AutoAttenuation

    def test_vsa_save_state(self):
        """Test save state queries instrument and calls os.system."""
        self.mock_vsa.query.return_value = "TEST_VAL"
        self.mock_vsa.queryInt.return_value = 160000000
        self.mock_vsa.s.getpeername.return_value = ("192.168.1.50", 5025)

        with patch('driver.OFDM_vsa_fsw.os.system') as mock_sys:
            self.driver.vsa_save_state()

            # self.mock_vsa.queryInt.assert_called_with(":TRAC:IQ:SRAT?")
            mock_sys.assert_called_once_with(r'start \\192.168.1.50\instr')

    # def test_vsa_load(self):
    #     """Test loading a state file onto the VSA."""
    #     filename = "C:\\R_S\\Instr\\user\\OFDM_setup.dfl"
    #     self.driver.vsa_load(filename)
    #     self.mock_vsa.write.assert_called_with(f"MMEM:LOAD:STAT 1, '{filename}'")

if __name__ == '__main__':
    unittest.main()
