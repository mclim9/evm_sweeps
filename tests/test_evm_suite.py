import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root and src to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))

from EVM_Suite import main  # noqa: E402

class TestEVM_Suite(unittest.TestCase):

    @patch('EVM_Suite.BenchConfig')
    @patch('EVM_Suite.VSA_driver')
    @patch('EVM_Suite.VSG_driver')
    @patch('EVM_Suite.SweepRunner')
    def test_main_initialization(self, mock_runner, mock_vsg_driver, mock_vsa_driver, mock_bench):
        """Verify that main() initializes drivers and starts the runner."""

        # Mock the bench starts
        mock_bench_inst = mock_bench.return_value
        mock_bench_inst.VSA_start.return_value = MagicMock()
        mock_bench_inst.VSG_start.return_value = MagicMock()

        main()

        # Verify bench was used to start instruments
        mock_bench_inst.VSA_start.assert_called()
        mock_bench_inst.VSG_start.assert_called()

        # Verify drivers were instantiated with the started instruments
        mock_vsa_driver.assert_called_once()
        mock_vsg_driver.assert_called_once()

        # Verify runner was created and executed at least once
        mock_runner.assert_called()
        mock_runner.return_value.run.assert_called()

if __name__ == '__main__':
    unittest.main()
