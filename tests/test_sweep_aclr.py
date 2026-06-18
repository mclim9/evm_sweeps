import unittest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
import sys
import os
import datetime

# Add project root and src to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))

from Sweep_ACLR import SweepConfig, SweepResultWriter, SweepRunner   # noqa: E402

class Test_Sweep_ACLR(unittest.TestCase):
    def setUp(self):
        self.config = SweepConfig(
            freq_arry=[2.4e9],
            pwr_arry=[-10, -5],
            lvl_arry=['LEV'],
            output_dir=Path('test_results'),
            file_prefix='test_sweep'
        )

    def test_sweep_config_output_path(self):
        """Verify that output_path creates a timestamped filename."""
        fixed_now = datetime.datetime(2023, 10, 27, 12, 0, 0)
        with patch('datetime.datetime') as mock_date:
            mock_date.now.return_value = fixed_now
            path = self.config.output_path()

            self.assertTrue(path.parent.exists())
            self.assertIn('test_sweep_20231027_120000.txt', str(path))

    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.mkdir')
    def test_sweep_result_writer(self, mock_mkdir, mock_file):
        """Verify SweepResultWriter opens file and writes lines."""
        path = Path('dummy/path.txt')
        writer = SweepResultWriter(path)

        writer.write_line("test data")
        mock_file().write.assert_called_with("test data\n")

        writer.close()
        mock_file().close.assert_called()

    @patch('EVM_Sweep.SweepResultWriter')
    def test_sweep_runner_execution_flow(self, mock_writer_class):
        """Verify that SweepRunner calls drivers and writer in correct order."""
        # Setup Mocks
        mock_vsa = MagicMock()
        mock_vsg = MagicMock()
        mock_writer = mock_writer_class.return_value

        # Mock instrument responses
        mock_vsa.VSA.idn = "FSW-IDN"
        mock_vsg.VSG.idn = "SMW-IDN"
        mock_vsa.vsa_get_waveform_info.return_value = "Waveform_Info_String"

        # method_timer decorated functions return (result, time)
        mock_vsa.vsa_set_level.return_value = (0.0, 0.5)
        mock_vsa.vsa_get_ACLR.return_value = ('123, 234, 345', 0.1)
        mock_vsa.vsa_get_attn_ref.return_value = ("10", 5.0, 20)
        mock_vsa.vsa_get_ch_power.return_value = -10.2
        mock_vsa.vsa_get_extra.return_value = "none"
        mock_vsg.vsg_get_extra.return_value = "none"

        runner = SweepRunner(mock_vsa, mock_vsg, self.config)
        runner.run()

        # Verify initial config
        mock_vsa.vsa_configure.assert_called_once()
        mock_vsg.vsg_configure.assert_called_once()

        # Verify Headers were written
        # mock_writer.write_line.assert_any_call("VSA: FSW-IDN")
        # mock_writer.write_line.assert_any_call("Waveform_Info_String")

        # Verify sweep logic (1 freq * 2 powers = 2 steps)
        self.assertEqual(mock_vsa.vsa_set_frequency.call_count, 1)
        self.assertEqual(mock_vsg.vsg_set_power.call_count, 2)
        self.assertEqual(mock_vsa.vsa_get_ACLR.call_count, 2)

        # Verify writer was closed
        # mock_writer.close.assert_called_once()

    @patch('EVM_Sweep.SweepResultWriter')
    def test_sweep_runner_step_calculation(self, mock_writer_class):
        """Verify the runner processes all combinations of freq/pwr/lvl."""
        config = SweepConfig(
            freq_arry=[2.4e9, 5.0e9],
            pwr_arry=[-20, -10, 0],
            lvl_arry=['LEV', 'EVM']
        )
        mock_vsa = MagicMock()
        mock_vsg = MagicMock()

        # Mock instrument attributes and responses used in loop formatting
        mock_vsa.VSA.idn = "VSA_IDN"
        mock_vsg.VSG.idn = "VSG_IDN"
        mock_vsa.vsa_get_waveform_info.return_value = "Waveform_Info"
        mock_vsa.vsa_set_level.return_value = (0.0, 0.1)
        mock_vsa.vsa_get_ACLR.return_value = ('123, 234, 345', 0.1)
        mock_vsa.vsa_get_attn_ref.return_value = ("10", 5.0, 30)
        mock_vsa.vsa_get_ch_power.return_value = -12.0
        mock_vsa.vsa_get_extra.return_value = 'none'
        mock_vsg.vsg_get_extra.return_value = 'none'

        runner = SweepRunner(mock_vsa, mock_vsg, config)

        with patch('logging.info') as mock_log:
            runner.run()
            # Total steps = 2 freqs * 3 powers * 2 levels = 12 steps
            # Check for the last step log
            mock_log.assert_any_call("12/12 done, estimated 0.00 min left")

if __name__ == '__main__':
    unittest.main()
