import unittest
from unittest.mock import MagicMock
import sys
import os

# Add src directory to path for imports
TEST_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(TEST_DIR, '..', 'src'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from driver.base_vsg import VSGDriver  # noqa: E402


class ConcreteVSGDriver(VSGDriver):
    """Concrete implementation for testing VSGDriver abstract base."""

    def vsg_configure(self) -> None:
        pass

    def vsg_save_state(self) -> None:
        pass

    def vsg_set_frequency(self, freq: float) -> None:
        pass

    def vsg_set_power(self, pwr: float) -> None:
        pass


class TestBaseVSG(unittest.TestCase):
    def test_abstract_class_cannot_be_instantiated(self):
        """Verify that VSGDriver cannot be instantiated directly due to abstract methods."""
        with self.assertRaises(TypeError):
            VSGDriver(MagicMock())

    def test_concrete_subclass_instantiation(self):
        """Verify that a subclass implementing all methods can be instantiated."""
        mock_vsg = MagicMock()
        driver = ConcreteVSGDriver(mock_vsg)
        self.assertEqual(driver.VSG, mock_vsg)

    def test_vsg_get_extra_default(self):
        """Verify the default implementation of vsg_get_extra returns 'none'."""
        driver = ConcreteVSGDriver(MagicMock())
        self.assertEqual(driver.vsg_get_extra(), "none")

if __name__ == '__main__':
    unittest.main()
