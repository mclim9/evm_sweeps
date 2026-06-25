from unittest.mock import MagicMock
import unittest
import sys
import os

TEST_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(TEST_DIR, '..', 'src'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from driver.VSG_util import set_SMW_K575

class Test_VSG_Util(unittest.TestCase):
    def test_set_smw_k575_off(self):
        vsg = MagicMock()
        set_SMW_K575(vsg, "OFF")

        vsg.write.assert_any_call(":SOUR1:CORR:OPT:RF:IQM 1")
        vsg.write.assert_any_call(":SOUR1:CORR:OPT:RF:HEAD 1")
        vsg.write.assert_any_call(":SOUR1:CORR:OPT:RF:LIN OFF")

    def test_set_smw_k575_on(self):
        vsg = MagicMock()
        set_SMW_K575(vsg, "ON")

        vsg.write.assert_any_call(":SOUR1:CORR:OPT:RF:IQM 1")
        vsg.write.assert_any_call(":SOUR1:CORR:OPT:RF:HEAD 1")
        vsg.query.assert_any_call(":SOUR1:CORR:OPT:RF:LIN AUTO;*OPC?")
        vsg.query.assert_any_call("*OPC?")

    def test_set_smw_k575_other_mode(self):
        vsg = MagicMock()
        set_SMW_K575(vsg, "UNKNOWN")

        vsg.write.assert_any_call(":SOUR1:CORR:OPT:RF:IQM 1")
        vsg.write.assert_any_call(":SOUR1:CORR:OPT:RF:HEAD 1")

if __name__ == '__main__':
    unittest.main()
