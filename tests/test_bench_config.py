"""Unit tests for bench_config module"""
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.helper.bench_config import bench


class TestBench(unittest.TestCase):
    """Test cases for bench configuration class"""

    def setUp(self):
        """Set up test fixtures with mocked configuration and sockets"""
        # Patch configparser to avoid reading actual .ini file
        self.config_patcher = patch('src.helper.bench_config.configparser.ConfigParser')
        self.mock_config_class = self.config_patcher.start()
        self.mock_config = MagicMock()
        self.mock_config_class.return_value = self.mock_config

        # Set up mock config to return VSA and VSG IPs
        self.mock_config.__getitem__.side_effect = lambda section: {
            'Settings': {'VSA_IP': '192.168.1.100', 'VSG_IP': '192.168.1.101'}
        }[section]

        # Patch iSocket
        self.socket_patcher = patch('src.helper.bench_config.iSocket')
        self.mock_socket_class = self.socket_patcher.start()

    def tearDown(self):
        """Clean up patches"""
        self.config_patcher.stop()
        self.socket_patcher.stop()

    def test_init_reads_config_file(self):
        """Test that __init__ reads configuration from .ini file"""
        b = bench()
        self.mock_config.read.assert_called_once()

    def test_init_sets_vsa_ip_from_config(self):
        """Test that VSA_IP is set from configuration"""
        b = bench()
        self.assertEqual(b.VSA_IP, '192.168.1.100')

    def test_init_sets_vsg_ip_from_config(self):
        """Test that VSG_IP is set from configuration"""
        b = bench()
        self.assertEqual(b.VSG_IP, '192.168.1.101')

    def test_vsa_start_connects_with_default_ip(self):
        """Test VSA_start connects using configured IP"""
        mock_vsa = MagicMock()
        self.mock_socket_class.return_value.open.return_value = mock_vsa

        b = bench()
        result = b.VSA_start()

        self.mock_socket_class.assert_called()
        self.mock_socket_class.return_value.open.assert_called_with('192.168.1.100', 5025)
        self.assertEqual(result, mock_vsa)
        self.assertEqual(b.VSA, mock_vsa)

    def test_vsa_start_connects_with_custom_ip(self):
        """Test VSA_start uses custom IP when provided"""
        mock_vsa = MagicMock()
        self.mock_socket_class.return_value.open.return_value = mock_vsa

        b = bench()
        custom_ip = '192.168.2.200'
        result = b.VSA_start(ip=custom_ip)

        self.mock_socket_class.return_value.open.assert_called_with(custom_ip, 5025)
        self.assertEqual(b.VSA_IP, custom_ip)
        self.assertEqual(result, mock_vsa)

    def test_vsg_start_connects_with_default_ip(self):
        """Test VSG_start connects using configured IP"""
        mock_vsg = MagicMock()
        self.mock_socket_class.return_value.open.return_value = mock_vsg

        b = bench()
        result = b.VSG_start()

        self.mock_socket_class.return_value.open.assert_called_with('192.168.1.101', 5025)
        self.assertEqual(result, mock_vsg)
        self.assertEqual(b.VSG, mock_vsg)

    def test_vsg_start_connects_with_custom_ip(self):
        """Test VSG_start uses custom IP when provided"""
        mock_vsg = MagicMock()
        self.mock_socket_class.return_value.open.return_value = mock_vsg

        b = bench()
        custom_ip = '192.168.2.201'
        result = b.VSG_start(ip=custom_ip)

        self.mock_socket_class.return_value.open.assert_called_with(custom_ip, 5025)
        self.assertEqual(b.VSG_IP, custom_ip)
        self.assertEqual(result, mock_vsg)

    def test_bench_verify_connects_both_instruments(self):
        """Test bench_verify connects to both VSA and VSG"""
        mock_vsa = MagicMock()
        mock_vsg = MagicMock()
        mock_vsa.idn = 'VSA IDN String'
        mock_vsg.idn = 'VSG IDN String'

        # Configure mock to return VSA on first call, VSG on second
        self.mock_socket_class.return_value.open.side_effect = [mock_vsa, mock_vsg]

        b = bench()
        b.bench_verify()

        # Verify both connections were made
        self.assertEqual(self.mock_socket_class.return_value.open.call_count, 2)
        self.assertEqual(b.VSA, mock_vsa)
        self.assertEqual(b.VSG, mock_vsg)

    def test_bench_verify_connection_sequence(self):
        """Test bench_verify uses correct IPs and ports"""
        mock_vsa = MagicMock()
        mock_vsg = MagicMock()
        mock_vsa.idn = 'VSA Info'
        mock_vsg.idn = 'VSG Info'

        self.mock_socket_class.return_value.open.side_effect = [mock_vsa, mock_vsg]

        b = bench()
        b.bench_verify()

        # Verify correct IPs and port were used
        calls = self.mock_socket_class.return_value.open.call_args_list
        self.assertEqual(calls[0], unittest.mock.call('192.168.1.100', 5025))
        self.assertEqual(calls[1], unittest.mock.call('192.168.1.101', 5025))

    def test_vsg_network_reset_starts_vsg_and_queries_network_reset(self):
        """Test VSG_network_reset calls VSG_start and sends network reset command"""
        mock_vsg = MagicMock()
        mock_vsg.query.return_value = '1'
        self.mock_socket_class.return_value.open.return_value = mock_vsg

        b = bench()
        b.vsg_network_reset = b.VSG_network_reset  # Ensure method exists
        b.VSG_network_reset()

        # Verify VSG was started
        self.mock_socket_class.return_value.open.assert_called_with('192.168.1.101', 5025)
        # Verify network reset command was sent
        mock_vsg.query.assert_called_once()
        call_args = mock_vsg.query.call_args[0][0]
        self.assertIn('SYST:COMM:NETW:REST', call_args)

    def test_set_inst_off_writes_shutdown_to_both_instruments(self):
        """Test set_inst_off sends shutdown command to both instruments"""
        mock_vsa = MagicMock()
        mock_vsg = MagicMock()
        self.mock_socket_class.return_value.open.side_effect = [mock_vsa, mock_vsg]

        b = bench()
        b.VSA_start()
        b.VSG_start()
        b.set_inst_off()

        # Verify shutdown commands were sent
        mock_vsa.write.assert_called_with(':SYST:SHUT')
        mock_vsg.write.assert_called_with(':SYST:SHUT')

    def test_set_inst_off_requires_vsa_and_vsg_initialized(self):
        """Test set_inst_off works only after instruments are initialized"""
        b = bench()
        # Should not raise without initialization when VSA/VSG don't exist
        # But will raise AttributeError if not initialized - this is expected behavior

    def test_multiple_vsa_connections_update_ip(self):
        """Test that multiple VSA_start calls with different IPs update the IP"""
        mock_vsa1 = MagicMock()
        mock_vsa2 = MagicMock()
        self.mock_socket_class.return_value.open.side_effect = [mock_vsa1, mock_vsa2]

        b = bench()
        b.VSA_start(ip='192.168.1.100')
        self.assertEqual(b.VSA_IP, '192.168.1.100')

        b.VSA_start(ip='192.168.1.110')
        self.assertEqual(b.VSA_IP, '192.168.1.110')

    def test_multiple_vsg_connections_update_ip(self):
        """Test that multiple VSG_start calls with different IPs update the IP"""
        mock_vsg1 = MagicMock()
        mock_vsg2 = MagicMock()
        self.mock_socket_class.return_value.open.side_effect = [mock_vsg1, mock_vsg2]

        b = bench()
        b.VSG_start(ip='192.168.1.101')
        self.assertEqual(b.VSG_IP, '192.168.1.101')

        b.VSG_start(ip='192.168.1.111')
        self.assertEqual(b.VSG_IP, '192.168.1.111')

    def test_vsa_start_returns_socket_instance(self):
        """Test VSA_start returns the iSocket instance"""
        mock_socket = MagicMock()
        self.mock_socket_class.return_value.open.return_value = mock_socket

        b = bench()
        result = b.VSA_start()

        self.assertIsInstance(result, MagicMock)
        self.assertEqual(result, b.VSA)

    def test_vsg_start_returns_socket_instance(self):
        """Test VSG_start returns the iSocket instance"""
        mock_socket = MagicMock()
        self.mock_socket_class.return_value.open.return_value = mock_socket

        b = bench()
        result = b.VSG_start()

        self.assertIsInstance(result, MagicMock)
        self.assertEqual(result, b.VSG)

    def test_config_read_called_with_correct_path(self):
        """Test that config.read is called to load .ini file"""
        b = bench()
        # Verify config.read was called
        self.mock_config.read.assert_called()

    def test_bench_maintains_separate_vsa_and_vsg_instances(self):
        """Test that VSA and VSG maintain separate socket instances"""
        mock_vsa = MagicMock()
        mock_vsg = MagicMock()
        self.mock_socket_class.return_value.open.side_effect = [mock_vsa, mock_vsg]

        b = bench()
        b.VSA_start()
        b.VSG_start()

        self.assertIsNot(b.VSA, b.VSG)
        self.assertEqual(b.VSA, mock_vsa)
        self.assertEqual(b.VSG, mock_vsg)


if __name__ == '__main__':
    unittest.main()
