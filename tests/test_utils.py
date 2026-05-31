from unittest.mock import MagicMock
import numpy as np
import unittest
import sys
import os

TEST_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(TEST_DIR, '..', 'src'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from helper.utils import get_Array_stats, method_timer, vsa_meas_EVM

class TestUtils(unittest.TestCase):
    def test_get_Array_stats(self):
        """Test calculation and string formatting of array statistics."""
        data = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
        # Expected values: Min: 10, Max: 50, Avg: 30, StdDev: 14.142, Delta: 40
        result = get_Array_stats(data)

        self.assertIsInstance(result, str)
        self.assertIn("Min:10.000", result)
        self.assertIn("Max:50.000", result)
        self.assertIn("Avg:30.000", result)
        self.assertIn("Delta:40.000", result)

    def test_method_timer_decorator(self):
        """Verify that the method_timer decorator returns (result, time)."""
        @method_timer
        def sample_function(a, b):
            return a + b

        result, elapsed = sample_function(5, 7)

        self.assertEqual(result, 12)
        self.assertIsInstance(elapsed, float)
        self.assertGreater(elapsed, 0)

    def test_vsa_meas_EVM_calls(self):
        """Verify that vsa_meas_EVM calls the expected driver methods in order."""
        mock_driver = MagicMock()
        vsa_meas_EVM(mock_driver)

        mock_driver.vsa_configure.assert_called_once()
        mock_driver.vsa_set_frequency.assert_called_with(6e9)
        mock_driver.vsa_sweep.assert_called_once()
        mock_driver.vsa_set_level.assert_called_with('MAN')
        mock_driver.vsa_get_evm.assert_called_once()

if __name__ == '__main__':
    unittest.main()
