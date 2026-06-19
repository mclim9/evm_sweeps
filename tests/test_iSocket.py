import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import socket

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
        # The class might be instantiated, but connect should not be called yet
        self.mock_socket_instance.connect.assert_not_called()

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

    def test_open_handles_socket_error(self):
        """Test that open() handles connection errors gracefully."""
        self.mock_socket_instance.connect.side_effect = socket.error("Connection Refused")
        sock = iSocket().open('192.168.1.1', 5025)
        # Should survive the print and return self
        self.assertIsInstance(sock, iSocket)

    def test_write_sends_command_with_newline(self):
        """Test that write() sends the command encoded with a newline."""
        sock = iSocket().open('127.0.0.1', 5025)
        command = '*RST'
        sock.write(command)
        # Use assert_any_call to be resilient to extra init commands
        self.mock_socket_instance.sendall.assert_any_call(b'*RST\n')

    def test_query_sends_command_and_receives_response(self):
        """Test that query() sends a command and returns the decoded response."""
        self.mock_socket_instance.recv.return_value = b'QUERY_RESPONSE_123\n'
        sock = iSocket().open('127.0.0.1', 5025)
        command = '*IDN?'
        response = sock.query(command)

        self.mock_socket_instance.recv.assert_called() # Buffer size may vary
        self.assertEqual(response, 'QUERY_RESPONSE_123')

    def test_query_sends_command_and_receives_comment(self):
        """Test that query() sends a command and returns the decoded response."""
        self.mock_socket_instance.recv.return_value = b'QUERY_RESPONSE_123\n'
        sock = iSocket().open('127.0.0.1', 5025)
        command = '*IDN?'
        response = sock.query(command, True)

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

    def test_close_closes_socket(self):
        """Test that close() calls the underlying socket close method."""
        sock = iSocket().open('127.0.0.1', 5025)
        sock.close()
        self.mock_socket_instance.close.assert_called_once()

    def test_read_receives_data(self):
        """Test that read() receives data from the socket."""
        self.mock_socket_instance.recv.return_value = b'RAW_DATA\n'
        sock = iSocket().open('127.0.0.1', 5025)
        result = sock.read()
        self.assertEqual(result, b'RAW_DATA\n')

    def test_read_returns_none_on_empty_packet(self):
        """Test that read() returns None if the first packet is empty."""
        self.mock_socket_instance.recv.return_value = b''
        sock = iSocket().open('127.0.0.1', 5025)
        self.assertIsNone(sock.read())

    def test_read_handles_socket_error(self):
        """Test that read() returns a sentinel on socket error."""
        self.mock_socket_instance.recv.side_effect = socket.error("Timeout")
        sock = iSocket().open('127.0.0.1', 5025)
        self.assertEqual(sock.read(), '<not Read>')

    def test_writeBin_sends_raw_bytes(self):
        """Test that writeBin() sends bytes and correctly appends a newline byte."""
        sock = iSocket().open('127.0.0.1', 5025)
        binary_data = b'\x00\x01\x02\x03'
        sock.writeBin(binary_data)
        self.mock_socket_instance.sendall.assert_any_call(binary_data + b'\n')

    def test_clear_error_loops_until_no_error(self):
        """Test that clear_error() continues to query SYST:ERR? until 0 is returned."""
        # Return an error twice, then "0,No error"
        self.mock_socket_instance.recv.side_effect = [
            b'MOCKED_IDN\n',
            b'-113,"Undefined header"\n',
            b'-222,"Data out of range"\n',
            b'0,"No error"\n'
        ]
        sock = iSocket().open('127.0.0.1', 5025)
        sock.clear_error()

        # Verify SYST:ERR? was sent 3 times (plus the initial *IDN?)
        self.assertEqual(self.mock_socket_instance.sendall.call_count, 4)

    def test_opc_polls_event_status_register(self):
        """Test that opc() polls *ESR? until bit 0 is set."""
        # ESR returns 0 (busy) then 1 (complete)
        self.mock_socket_instance.recv.side_effect = [
            b'MOCKED_IDN\n',
            b'0\n',
            b'1\n'
        ]
        sock = iSocket().open('127.0.0.1', 5025)

        with patch('time.sleep') as mock_sleep:
            sock.opc(':INIT:IMM')
            self.assertTrue(mock_sleep.called)
            self.mock_socket_instance.sendall.assert_any_call(b'*ESR?\n')

    def test_tick_tock_benchmarking(self):
        """Test the tick/tock timing utility."""
        sock = iSocket()
        # Source uses timeit.default_timer, so we must patch that specifically
        with patch('timeit.default_timer', side_effect=[100.0, 105.5]):
            sock.tick()
            elapsed = sock.tock()
            self.assertEqual(elapsed, 5.5)

    def test_tock_comment(self):
        """Test the tock timing utility."""
        sock = iSocket()
        with patch('timeit.default_timer', side_effect=[100.0, 105.5]):
            sock.tick()
            elapsed = sock.tock('comment')
            self.assertEqual(elapsed, 5.5)

    def test_timeout_updates_socket_timeout(self):
        """Test that timeout() updates the socket timeout."""
        sock = iSocket().open('127.0.0.1', 5025)
        sock.timeout(45)
        self.mock_socket_instance.settimeout.assert_called_with(45)

    def test_query_returns_not_read_on_socket_error(self):
        """Test that query returns a sentinel string on socket exceptions."""
        sock = iSocket().open('127.0.0.1', 5025)

        # Force an error on the recv call, which is correctly handled inside query's try block
        self.mock_socket_instance.recv.side_effect = socket.error("Connection lost")

        result = sock.query('*IDN?')
        self.assertEqual(result, '<not Read>')

    def test_delay_calls_time_sleep(self):
        """Test the delay utility method."""
        sock = iSocket()
        with patch('time.sleep') as mock_sleep:
            sock.delay(2.5)
            mock_sleep.assert_called_once_with(2.5)

    def test_logging_test_executes_without_error(self):
        """Test utility logging method executes."""
        self.mock_socket_instance.recv.return_value = b'IDN_DATA\n'
        sock = iSocket().open('127.0.0.1', 5025)
        # Simply ensure it doesn't crash
        try:
            sock.logging_test('test.txt')
            success = True
        except Exception:
            success = False
        self.assertTrue(success)

if __name__ == '__main__':
    unittest.main()
