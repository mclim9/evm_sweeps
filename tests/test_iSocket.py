import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import socket

TEST_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(TEST_DIR, '..', 'src')))

from src.helper.iSocket import iSocket  # noqa:


class TestiSocket(unittest.TestCase):
    def setUp(self):
        self.socket_patcher = patch('src.helper.iSocket.socket.socket')
        self.mock_socket_class = self.socket_patcher.start()
        self.mock_socket = MagicMock()
        self.mock_socket_class.return_value = self.mock_socket

        self.isocket = iSocket()

    def tearDown(self):
        self.socket_patcher.stop()

    def test_init_creates_socket(self):
        self.mock_socket_class.assert_called_once()

    def test_close_closes_socket(self):
        self.isocket.close()
        self.mock_socket.close.assert_called_once()

    def test_delay_sleeps_for_specified_time(self):
        with patch('src.helper.iSocket.time.sleep') as mock_sleep:
            self.isocket.delay(2.5)
            mock_sleep.assert_called_once_with(2.5)

    def test_logging_test_creates_logger(self):
        with patch('src.helper.iSocket.logging.FileHandler') as mock_handler:
            logger = self.isocket.logging_test('test.log')
            self.assertIsNotNone(logger)
            mock_handler.assert_called_once_with('test.log')

    def test_open_connects_and_queries_idn(self):
        self.mock_socket.recv.return_value = b'Rohde & Schwarz,SMW200A,123456,1.0\n'

        with patch('src.helper.iSocket.logging.basicConfig'):
            result = self.isocket.open('192.168.1.1', 5025)

        self.mock_socket.connect.assert_called_once_with(('192.168.1.1', 5025))
        self.mock_socket.settimeout.assert_called_once_with(5)
        self.assertEqual(self.isocket.idn, 'Rohde & Schwarz,SMW200A,123456,1.0')
        self.assertEqual(result, self.isocket)

    def test_open_handles_socket_error(self):
        self.mock_socket.connect.side_effect = socket.error("Connection failed")

        with patch('src.helper.iSocket.logging.basicConfig'):
            with patch('builtins.print') as mock_print:
                result = self.isocket.open('192.168.1.1', 5025)  # noqa:
                mock_print.assert_called()

    def test_write_sends_scpi_command(self):
        with patch('src.helper.iSocket.logging.info'):
            self.isocket.write('*RST')

        self.mock_socket.sendall.assert_called_once_with('*RST\n'.encode())

    def test_write_bin_sends_binary_scpi(self):
        with patch('src.helper.iSocket.logging.info'):
            self.isocket.writeBin(b'*RST')

        self.mock_socket.sendall.assert_called_once_with(b'*RST' + bytes([10]))

    def test_query_writes_and_reads(self):
        self.mock_socket.recv.return_value = b'42\n'

        with patch('src.helper.iSocket.logging.info'):
            with patch('src.helper.iSocket.time.sleep'):
                result = self.isocket.query('*IDN?')

        self.assertEqual(result, '42')
        self.mock_socket.sendall.assert_called_once()

    def test_query_handles_socket_error(self):
        self.mock_socket.recv.side_effect = socket.error("Read failed")

        with patch('src.helper.iSocket.logging.info'):
            with patch('src.helper.iSocket.time.sleep'):
                result = self.isocket.query('*IDN?')

        self.assertEqual(result, '<not Read>')

    def test_queryInt_converts_to_int(self):
        self.mock_socket.recv.return_value = b'123\n'

        with patch('src.helper.iSocket.logging.info'):
            with patch('src.helper.iSocket.time.sleep'):
                result = self.isocket.queryInt('*ESR?')

        self.assertEqual(result, 123)
        self.assertIsInstance(result, int)

    def test_queryFloat_converts_to_float(self):
        self.mock_socket.recv.return_value = b'3.14159\n'

        with patch('src.helper.iSocket.logging.info'):
            with patch('src.helper.iSocket.time.sleep'):
                result = self.isocket.queryFloat(':FETC:POW?')

        self.assertEqual(result, 3.14159)
        self.assertIsInstance(result, float)

    def test_timeout_sets_socket_timeout(self):
        self.isocket.timeout(10)
        self.mock_socket.settimeout.assert_called_with(10)

    def test_tick_and_tock_measure_time(self):
        with patch('src.helper.iSocket.timeit.default_timer') as mock_timer:
            mock_timer.side_effect = [1.0, 1.5]

            self.isocket.tick()
            elapsed = self.isocket.tock()

            self.assertAlmostEqual(elapsed, 0.5)

    def test_tick_and_tock_with_comment(self):
        with patch('src.helper.iSocket.timeit.default_timer') as mock_timer:
            mock_timer.side_effect = [1.0, 1.25]

            with patch('builtins.print') as mock_print:
                self.isocket.tick()
                self.isocket.tock('test operation')
                mock_print.assert_called_once()

    def test_read_receives_data(self):
        self.mock_socket.recv.return_value = b'test data\n'

        result = self.isocket.read()

        self.assertEqual(result, b'test data\n')

    def test_read_handles_multiple_packets(self):
        self.mock_socket.recv.side_effect = [
            b'packet1',
            b'packet2\n'
        ]

        result = self.isocket.read()

        self.assertEqual(result, b'packet1packet2\n')

    def test_read_handles_socket_error(self):
        self.mock_socket.recv.side_effect = socket.error("Read failed")

        result = self.isocket.read()

        self.assertEqual(result, '<not Read>')

    def test_read_handles_empty_packet(self):
        self.mock_socket.recv.side_effect = [b'']

        result = self.isocket.read()

        self.assertIsNone(result)

    def test_clear_error_clears_errors(self):
        self.mock_socket.recv.side_effect = [
            b'401,"Query FIFO Overflow"\n',
            b'0,"No error"\n'
        ]

        with patch('src.helper.iSocket.logging.info'):
            with patch('src.helper.iSocket.time.sleep'):
                with patch('builtins.print'):
                    num_errors = self.isocket.clear_error()

        self.assertEqual(num_errors, 1)

    def test_clear_error_all_errors_cleared(self):
        self.mock_socket.recv.side_effect = [
            b'0,"No error"\n'
        ]

        with patch('src.helper.iSocket.logging.info'):
            with patch('src.helper.iSocket.time.sleep'):
                with patch('builtins.print'):
                    num_errors = self.isocket.clear_error()

        self.assertEqual(num_errors, 0)


if __name__ == '__main__':
    unittest.main()
