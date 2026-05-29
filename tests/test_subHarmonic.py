import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import numpy as np

# Add src and helper directories to path for imports
TEST_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(TEST_DIR, '..', 'src'))
HELPER_DIR = os.path.join(SRC_DIR, 'helper')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if HELPER_DIR not in sys.path:
    sys.path.insert(0, HELPER_DIR)

import driver.subHarmonic as subHarmonic
from driver.subHarmonic import option_functions

class TestSubHarmonic(unittest.TestCase):
    def setUp(self):
        # Set global variables that the module expects
        subHarmonic.frequncy = 6e9
        subHarmonic.swp_time = 1.0

        # Patch bench to avoid real socket connections
        self.bench_patcher = patch('driver.subHarmonic.bench')
        self.mock_bench_class = self.bench_patcher.start()

        # Mock VSA and VSG instruments
        self.mock_vsa = MagicMock()
        self.mock_vsa.s = MagicMock()
        self.mock_vsg = MagicMock()

        self.mock_bench_instance = self.mock_bench_class.return_value
        self.mock_bench_instance.VSA_start.return_value = self.mock_vsa
        self.mock_bench_instance.VSG_start.return_value = self.mock_vsg

        # Instantiate the class under test
        self.options = option_functions()

    def tearDown(self):
        self.bench_patcher.stop()

    def test_init_starts_instruments(self):
        """Verify VSA and VSG are started during init."""
        self.mock_bench_instance.VSA_start.assert_called_once()
        self.mock_bench_instance.VSG_start.assert_called_once()
        self.mock_vsa.s.settimeout.assert_called_with(30)

    def test_VSA_Config_sends_correct_commands(self):
        """Verify the SCPI sequence for VSA Spectrum configuration."""
        # VSA_Config is decorated with method_timer
        _, elapsed = self.options.VSA_Config()
        
        self.mock_vsa.query.assert_any_call('*RST;*OPC?')
        self.mock_vsa.query.assert_any_call(':INST:SEL "Spectrum";*OPC?')
        self.mock_vsa.write.assert_any_call(':SENS:FREQ:CENT 6000000000.0')
        self.mock_vsa.write.assert_any_call(':INP:ATT 0')
        self.mock_vsa.clear_error.assert_called_once()
        self.assertIsInstance(elapsed, float)

    def test_STN_Noise_Marker(self):
        """Verify noise marker settings."""
        self.options.STN_Noise_Marker()
        self.mock_vsa.write.assert_any_call(':SENS:WIND1:DET1:FUNC RMS')
        self.mock_vsa.write.assert_any_call(':CALC1:MARK1:FUNC:NOIS:STAT ON')
        self.mock_vsa.write.assert_any_call(':CALC1:MARK1:X 6000000000.0')

    def test_get_VSA_sweep_noise_mkr(self):
        """Verify sweep trigger and noise marker query."""
        self.mock_vsa.queryFloat.return_value = -110.5
        
        # get_VSA_sweep_noise_mkr is decorated with method_timer
        marker_val, elapsed = self.options.get_VSA_sweep_noise_mkr()
        
        self.mock_vsa.write.assert_called_with('INIT:CONT OFF')
        self.mock_vsa.query.assert_called_with('INIT:IMM;*OPC?')
        self.assertEqual(marker_val, -110.5)
        self.assertIsInstance(elapsed, float)

    def test_get_Array_stats(self):
        """Test statistical calculation and string output."""
        data = np.array([10, 20, 30])
        # Mean: 20, Min: 10, Max: 30, Delta: 20
        result = self.options.get_Array_stats(data)
        
        self.assertIsInstance(result, str)
        self.assertIn("Avg:20.000", result)
        self.assertIn("Delta:20.000", result)

if __name__ == '__main__':
    unittest.main()
