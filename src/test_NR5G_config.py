import unittest
from NR5G_config import config


class TestGeneral(unittest.TestCase):
    def setUp(self):
        '''Run before every test'''
        self.config = config()

    def tearDown(self):
        '''Run after every test'''
        err = self.config.VSA.query('SYST:ERR?')
        self.assertEqual(err.split(',')[0], '0')
        self.config.VSA.close()
        self.config.VSG.close()

    def test_VSG_Config(self):
        self.config.VSG_Config()

    def test_VSA_Config(self):
        self.config.VSA_Config()


if __name__ == '__main__':
    # coverage run -a -m unittest -b -v test_NR5G_config
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGeneral)
    unittest.TextTestRunner(verbosity=2).run(suite)
