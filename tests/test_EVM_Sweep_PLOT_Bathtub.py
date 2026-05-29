import unittest
from unittest.mock import patch
import os
import sys
import pandas as pd
import warnings

# Add project root and src to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from EVM_Sweep_PLOT_Bathtub import plotter  # noqa: E402


class TestEVM_Sweep_PLOT_Bathtub(unittest.TestCase):
    """Unit tests for the plotter class in EVM_Sweep_PLOT_Bathtub."""

    def setUp(self):
        """Set up mock data for testing."""
        # Suppress Matplotlib legend warnings during tests to keep logs clean
        warnings.filterwarnings("ignore", category=UserWarning, message="No artists with labels found")

        # Mock header dataframe (3 rows)
        self.header_data = pd.DataFrame({
            0: ["VSA:", "VSG:", "Waveform_Info"],
            1: ["FSW_Model", "SMW_Model", "None"]
        })

        # Mock measurement data
        self.csv_data = pd.DataFrame({
            "Date": ["2023/10/27", "2023/10/27"],
            "Time": ["12:00:00", "12:00:01"],
            "Freq": [1e9, 2e9],  # Use different frequencies for per_freq tests
            "Power[dBm]": [-10.0, -5.0],
            "RefLvl[dBm]": [5.0, 5.0],
            "Attn[dB]": [10, 10],
            "ChPwr[dBm]": [-10.2, -5.1],
            "EVM[dB]": ["-45.5", "-42.1"],  # Strings to test float conversion
            "Leveling": ["MAN", "MAN"],
            "AL-Time": [0.1, 0.1],
            "EVMT": [0.2, 0.2],
            "TotalTime": [0.3, 0.3],
            "VSA_extra": ["none", "none"],
            "VSG_extra": ["none", "none"]
        })

    @patch("EVM_Sweep_PLOT_Bathtub.pd.read_csv")
    @patch("EVM_Sweep_PLOT_Bathtub.plt.savefig")
    def test_read_data_initialization(self, _mock_savefig, mock_read_csv):
        """Test that data is correctly read and augmented from the header."""
        # Mock calls for header then data
        mock_read_csv.side_effect = [self.header_data, self.csv_data]

        p = plotter(filename="results.txt")

        # Verify columns added from header
        self.assertEqual(p.df["VSA"].iloc[0], "FSW_Model")
        self.assertEqual(p.df["VSG"].iloc[0], "SMW_Model")
        self.assertEqual(p.df["wave"].iloc[0], "Waveform_Info")

        # Verify float conversion of EVM column
        self.assertIsInstance(p.df["EVM[dB]"].iloc[0], float)
        self.assertEqual(p.df["EVM[dB]"].iloc[0], -45.5)

    @patch("EVM_Sweep_PLOT_Bathtub.pd.read_csv")
    @patch("EVM_Sweep_PLOT_Bathtub.plt.savefig")
    def test_filter_data_bathtub(self, mock_savefig, mock_read_csv):
        """Test the bathtub filtering and pivot table creation."""
        mock_read_csv.side_effect = [self.header_data, self.csv_data]
        p = plotter(filename="results.txt")

        p.filter_data_bathtub()

        # Check if table is created with correct index
        self.assertFalse(p.table.empty)
        self.assertEqual(p.table.index.name, "Power[dBm]")
        self.assertEqual(len(p.table), 2)  # Two power levels

        # Check if savefig was called
        self.assertTrue(mock_savefig.called)
        filename_called = mock_savefig.call_args[0][0]
        self.assertIn("bathtub.png", filename_called)

    @patch("EVM_Sweep_PLOT_Bathtub.pd.read_csv")
    @patch("EVM_Sweep_PLOT_Bathtub.plt.savefig")
    def test_filter_data_bathtub_per_freq(self, mock_savefig, mock_read_csv):
        """Test the bathtub per frequency filtering and plotting."""
        # Provide 4 items in side_effect in case the method re-reads data
        mock_read_csv.side_effect = [
            self.header_data, self.csv_data,
            self.header_data, self.csv_data
        ]
        p = plotter(filename="results.txt")

        p.filter_data_bathtub_per_freq()

        # Verify that savefig was called, likely producing a per-frequency bathtub plot
        mock_savefig.assert_called()
        filename_called = mock_savefig.call_args[0][0]
        self.assertIn("results_bathtub_2.000GHz.png", filename_called)

    @patch("EVM_Sweep_PLOT_Bathtub.pd.read_csv")
    @patch("EVM_Sweep_PLOT_Bathtub.plt.savefig")
    def test_filter_data_freqResp(self, mock_savefig, mock_read_csv):
        """Test the frequency response filtering and plotting."""
        # Provide 4 items in side_effect in case the method re-reads data
        mock_read_csv.side_effect = [
            self.header_data, self.csv_data,
            self.header_data, self.csv_data
        ]
        p = plotter(filename="results.txt")

        p.filter_data_freqResp()

        # Verify that savefig was called for the frequency response plot
        mock_savefig.assert_called()
        filename_called = mock_savefig.call_args[0][0]
        self.assertIn("results_freqResp_12.png", filename_called)

    @patch("EVM_Sweep_PLOT_Bathtub.tk.Tk")
    @patch("EVM_Sweep_PLOT_Bathtub.filedialog.askopenfilenames")
    @patch("EVM_Sweep_PLOT_Bathtub.pd.read_csv")
    def test_select_file_loop(self, mock_read_csv, mock_ask, mock_tk):
        """Test selection of multiple files via GUI prompt."""
        mock_ask.return_value = ["file1.txt", "file2.txt"]
        # 2 files * 2 read_csv calls per file = 4 calls total
        mock_read_csv.side_effect = [
            self.header_data, self.csv_data,
            self.header_data, self.csv_data
        ]

        p = plotter()  # Triggers select_file() constructor path

        # DataFrame should contain combined data from both files
        self.assertEqual(len(p.df), 4)
        self.assertTrue(mock_tk.called)

    def test_convert_column_to_float_missing_column(self):
        """Test that missing columns are handled gracefully."""
        # Bypass init to test method in isolation
        with patch("EVM_Sweep_PLOT_Bathtub.plotter.read_data"):
            p = plotter(filename="dummy.txt")
            df = pd.DataFrame({"A": [1, 2]})

            # Should not raise exception even if column "B" doesn't exist
            result = p.convert_column_to_float(df, "B")
            self.assertEqual(list(result.columns), ["A"])


if __name__ == "__main__":
    unittest.main()
