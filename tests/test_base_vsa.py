import unittest
from unittest.mock import MagicMock
import sys
import os

# Add src directory to path for imports
TEST_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(TEST_DIR, '..', 'src'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from driver.base_vsa import VSADriver

class ConcreteVSADriver(VSADriver):
    """Concrete implementation for testing VSADriver abstract base."""
    def vsa_configure(self) -> None: pass
    def vsa_get_ACLR(self) -> float: return 0.0
    def vsa_get_attn_ref(self): return ("0", 0.0)
    def vsa_get_evm(self): return (0.0, 0.0)
    def vsa_get_ch_power(self) -> float: return 0.0
    def vsa_get_waveform_info(self) -> str: return "test"
    def vsa_set_frequency(self, freq: float) -> None: pass
    def vsa_set_level(self, mode: str) -> float: return 0.0

class TestBaseVSA(unittest.TestCase):
    def test_abstract_class_cannot_be_instantiated(self):
        """Verify that VSADriver cannot be instantiated directly due to abstract methods."""
        with self.assertRaises(TypeError):
            VSADriver(MagicMock(), MagicMock())

    def test_concrete_subclass_instantiation(self):
        """Verify that a subclass implementing all methods can be instantiated."""
        mock_vsa = MagicMock()
        mock_vsg = MagicMock()
        driver = ConcreteVSADriver(mock_vsa, mock_vsg)
        self.assertEqual(driver.VSA, mock_vsa)
        self.assertEqual(driver.VSG, mock_vsg)

    def test_vsa_get_extra_default(self):
        """Verify the default implementation of vsa_get_extra returns 'none'."""
        driver = ConcreteVSADriver(MagicMock(), MagicMock())
        self.assertEqual(driver.vsa_get_extra(), "none")


if __name__ == '__main__':
    unittest.main()
