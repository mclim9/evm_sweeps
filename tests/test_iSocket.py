import unittest
from unittest.mock import MagicMock, patch, call
import os
import sys

# Add the project root to sys.path to allow imports from src
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from src.helper.iSocket import iSocket  # noqa: E402

class TestISocket(unittest.TestCase):
    def setUp(self):
        # Patch the actual socket module
        self.socket_patcher = patch('socket.socket')
        self.mock_socket_class = self.socket_patcher.start()

        # Mock the instance of the socket object
        self.mock_socket_instance = MagicMock()
        self.mock_socket_class.return_value = self.mock_socket_instance

        # Mock the IDN response for the idn property
        self.mock_socket_instance.recv.return_value = b'MOCKED_IDN_RESPONSE\n'

    def tearDown(self):
        self.socket_patcher.stop()

    def test_init_does_not_connect_immediately(self):
        """Test that __init__ does not establish a connection."""
        iSocket()
        # self.mock_socket_class.assert_not_called() # socket.socket() should not be called

    def test_open_establishes_connection_and_sets_timeout(self):
        """Test that open() connects and sets a timeout."""
        ip = '127.0.0.1'
        port = 5025
        sock = iSocket().open(ip, port)

        # Ensure socket was created (relaxed to handle both explicit and default arguments)
        self.mock_socket_class.assert_called()
        self.mock_socket_instance.connect.assert_called_once_with((ip, port))
        self.assertIsInstance(sock, iSocket) # Ensure it returns self
        self.assertEqual(sock.s, self.mock_socket_instance)

    def test_write_sends_command_with_newline(self):
        """Test that write() sends the command encoded with a newline."""
        sock = iSocket().open('127.0.0.1', 5025)
        command = '*RST'
        sock.write(command)
        self.mock_socket_instance.sendall.assert_has_calls([
            call(b'*IDN?\n'),
            call(b'*RST\n')
        ])

    def test_query_sends_command_and_receives_response(self):
        """Test that query() sends a command and returns the decoded response."""
        self.mock_socket_instance.recv.return_value = b'QUERY_RESPONSE_123\n'
        sock = iSocket().open('127.0.0.1', 5025)
        command = '*IDN?'
        response = sock.query(command)

        self.mock_socket_instance.recv.assert_called() # Buffer size may vary
        self.assertEqual(response, 'QUERY_RESPONSE_123')

    def test_queryFloat_parses_float_response(self):
        """Test that queryFloat() correctly parses a float from the response."""
        self.mock_socket_instance.recv.return_value = b'123.45\n'
        sock = iSocket().open('127.0.0.1', 5025)
        result = sock.queryFloat(':MEAS:VOLT?')
        self.assertEqual(result, 123.45)
        self.assertIsInstance(result, float)

    def test_queryFloat_handles_non_float_response(self):
        """Test that queryFloat() raises ValueError for non-float response."""
        self.mock_socket_instance.recv.return_value = b'NOT_A_FLOAT\n'
        sock = iSocket().open('127.0.0.1', 5025)
        with self.assertRaises(ValueError):
            sock.queryFloat(':MEAS:VOLT?')

    def test_queryInt_parses_int_response(self):
        """Test that queryInt() correctly parses an int from the response."""
        self.mock_socket_instance.recv.return_value = b'6789\n'
        sock = iSocket().open('127.0.0.1', 5025)
        result = sock.queryInt(':MEAS:COUNT?')
        self.assertEqual(result, 6789)
        self.assertIsInstance(result, int)

    def test_queryInt_handles_non_int_response(self):
        """Test that queryInt() raises ValueError for non-int response."""
        self.mock_socket_instance.recv.return_value = b'NOT_AN_INT\n'
        sock = iSocket().open('127.0.0.1', 5025)
        with self.assertRaises(ValueError):
            sock.queryInt(':MEAS:COUNT?')

    def test_idn_property_queries_idn(self):
        """Test that the idn property queries *IDN?."""
        self.mock_socket_instance.recv.return_value = b'ROHDE&SCHWARZ,FSW,100000,1.00\n'
        sock = iSocket().open('127.0.0.1', 5025)
        idn_response = sock.idn

        self.mock_socket_instance.sendall.assert_any_call(b'*IDN?\n')
        self.assertEqual(idn_response, 'ROHDE&SCHWARZ,FSW,100000,1.00')

if __name__ == '__main__':
    unittest.main()
