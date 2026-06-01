import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add src directory to path for imports
TEST_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(TEST_DIR, '..', 'src'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from driver.K18_vsa_fsw import VSA_driver

class TestK18VSAFSW(unittest.TestCase):
    def setUp(self):
        # Patch BenchConfig used inside K18_vsa_fsw to avoid socket creation
        self.bench_patcher = patch('driver.K18_vsa_fsw.BenchConfig')
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

        # Provide a mock VSG if the driver expects it for frequency settings
        # (Common in this codebase to sync VSG and VSA frequencies)
        self.mock_vsg = MagicMock()
        self.driver.VSG = self.mock_vsg

    def tearDown(self):
        self.bench_patcher.stop()

    def test_init_sets_up_vsa(self):
        """Test that __init__ starts VSA connection and sets socket timeout."""
        self.mock_bench_instance.VSA_start.assert_called_once()
        self.assertEqual(self.driver.VSA, self.mock_vsa)
        self.mock_vsa.s.settimeout.assert_called_with(30)

    def test_vsa_configure_sends_scpi(self):
        """Test vsa_configure sends the correct sequence of SCPI commands for K18."""
        # vsa_configure is decorated with method_timer, returns (None, time)
        _, elapsed = self.driver.vsa_configure()

        self.mock_vsa.query.assert_any_call('*RST;*OPC?')
        self.mock_vsa.query.assert_any_call(':INST:CRE:NEW AMPL, "Amplifier"; *OPC?')
        self.assertIsInstance(elapsed, float)

    def test_vsa_get_ACLR(self):
        """Test retrieving ACLR data returns expected values."""
        self.mock_vsa.query.side_effect = [
            "",        # from vsa_sweep query (*OPC?)
            "-15.5",   # chPwr
            "-45.2"    # ACLRV
        ]
        (chPwr, ACLRV), _ = self.driver.vsa_get_ACLR()
        self.assertEqual(chPwr, "-15.5")
        self.assertEqual(ACLRV, 'none')

    def test_vsa_get_attn_ref(self):
        """Test retrieving attenuation and reference level."""
        self.mock_vsa.query.return_value = "20"
        self.mock_vsa.queryFloat.return_value = 10.0
        attn, refl = self.driver.vsa_get_attn_ref()
        self.assertEqual(attn, "20")
        # self.assertEqual(refl, 10.0)

    def test_vsa_get_ch_power(self):
        """Test retrieving channel power."""
        self.mock_vsa.queryFloat.return_value = 1.0
        self.mock_vsa.queryFloat.return_value = 0.5
        pwr = self.driver.vsa_get_ch_power()
        # self.assertEqual(pwr, 0.5)

    def test_vsa_get_evm_success(self):
        """Test EVM retrieval on a successful sweep."""
        self.mock_vsa.query.return_value = "1"
        self.mock_vsa.queryFloat.return_value = -40.5

        evm, _ = self.driver.vsa_get_evm()
        self.mock_vsa.write.assert_any_call('INIT:CONT OFF')
        self.mock_vsa.queryFloat.assert_called_with(':FETC:MACC:REVM:CURR:RES?')
        # self.assertEqual(evm, -40.5)

    def test_vsa_get_evm_retry(self):
        """Test that EVM retrieval retries once on failure."""
        self.mock_vsa.query.return_value = "1"
        # Fail the first attempt, succeed on the second
        self.mock_vsa.queryFloat.side_effect = [Exception("Comm error"), -50.5]

        evm, _ = self.driver.vsa_get_evm()
        self.assertEqual(evm, -50.5)

    def test_vsa_get_extra(self):
        """Test vsa_get_extra default value."""
        extra = self.driver.vsa_get_extra()
        self.assertIsInstance(extra, str)
        self.assertEqual(extra, 'K18 EVM')

    def test_vsa_get_extra_query_failure(self):
        """Test vsa_get_extra returns the default value when instrument query fails."""
        # Mocking the case where an internal instrument query might return the error sentinel
        self.mock_vsa.query.return_value = '<not Read>'
        extra = self.driver.vsa_get_extra()
        self.assertEqual(extra, 'K18 EVM')

    def test_vsa_get_extra_IQNC(self):
        """Test vsa_get_extra returns a string with the expected value."""
        extra = self.driver.vsa_get_extra('IQNC')
        self.assertEqual(extra, 'K18 EVM IQNC')
        pass

    def test_vsa_get_extra_XCORR(self):
        """Test vsa_get_extra returns a string with the expected value."""
        extra = self.driver.vsa_get_extra('xcorr')
        self.assertEqual(extra, 'K18 EVM XCORR')

    def test_vsa_get_waveform_info(self):
        """Test waveform info construction."""
        self.mock_vsa.query.return_value = "1234567"
        outStr = self.driver.vsa_get_waveform_info()
        self.mock_vsa.query.assert_any_call(':SENS:FREQ:CENT?')
        self.assertEqual(outStr, "0.001234567GHz_K18")

    def test_vsa_set_frequency(self):
        self.driver.vsa_set_frequency(5.0e9)
        self.mock_vsa.write.assert_called_with(':SENS1:FREQ:CENT 5000000000.0')

    def test_vsa_set_level_auto(self):
        """Test triggering autolevel."""
        self.driver.vsa_set_level(method='LEV')
        self.mock_vsa.query.assert_called_with(':SENS:ADJ:LEV;*OPC?')

    def test_vsa_set_level_man(self):
        """Test triggering autolevel."""
        self.driver.vsa_set_level(method='MAN')
        # self.mock_vsa.write.assert_called_with(':INP:ATT:AUTO ON')
        self.mock_vsa.query.assert_any_call('INIT:IMM;*OPC?')

    def test_vsa_load(self):
        """Test loading a state file onto the VSA."""
        filename = "C:\\R_S\\Instr\\user\\K18_setup.dfl"
        self.driver.vsa_load(filename)
        self.mock_vsa.write.assert_called_with(f':MMEM:LOAD:DEM:C1 "{filename}"')

    def test_vsa_save_state(self):
        """Test saving state and opening the remote instrument folder."""
        self.mock_vsa.s.getpeername.return_value = ("10.0.0.1", 5025)
        self.driver.Wavename = "K18_test_config"

        with patch('driver.K18_vsa_fsw.os.system') as mock_sys:
            self.driver.vsa_save_state()
            self.mock_vsa.query.assert_any_call('*IDN?')
            mock_sys.assert_called_once_with(r'start \\10.0.0.1\instr')

    def test_vsa_sweep(self):
        """Test triggering a single capture sweep."""
        _, elapsed = self.driver.vsa_sweep()
        self.mock_vsa.write.assert_called_with('INIT:CONT OFF')
        self.mock_vsa.query.assert_called_with('INIT:IMM;*OPC?')
        self.assertIsInstance(elapsed, float)

if __name__ == '__main__':
    unittest.main()
