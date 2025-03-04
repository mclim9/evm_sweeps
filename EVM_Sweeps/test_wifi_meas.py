import unittest
from iSocket import iSocket
from WiFi_meas import option_functions
from bench_config import bench

class TestGeneral(unittest.TestCase):
    def setUp(self):
        '''Run before every test'''
        self.meas = option_functions()

    def tearDown(self):
        '''Run after every test'''
        err = self.meas.VSA.query('SYST:ERR?')
        self.assertEqual(err.split(',')[0], '0')
        self.meas.VSA.close()
        self.meas.VSG.close()

    def test_get_ACLR(self):
        self.meas.get_ACLR()

    def test_get_EVM(self):
        self.meas.get_EVM()

    def test_get_info(self):
        self.meas.get_info()

    def test_get_Ch_Pwr(self):
        self.meas.get_ChPwr()

    def test_set_level_autolevel(self):
        self.meas.set_VSA_level('LEV')

    def test_set_freq(self):
        self.meas.set_freq(18e6)

    def test_set_VSA_init(self):
        self.meas.set_VSA_init()

    def test_set_VSG_init(self):
        self.meas.set_VSG_init()


if __name__ == '__main__':
    # coverage run -a -m unittest -b -v test_HW_VSA_Common
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGeneral)
    unittest.TextTestRunner(verbosity=2).run(suite)
