import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from unittest.mock import MagicMock, patch, call
from src.driver import NR5G_FR2_meas

mock_bench = patch('src.driver.NR5G_FR2_meas.bench')
mock_bench = mock_bench.start()
mock_vsa = MagicMock()
mock_vsa.s = MagicMock()
mock_vsg = MagicMock()
mock_bench.return_value.VSA_start.return_value = mock_vsa
mock_bench.return_value.VSG_start.return_value = mock_vsg

driver = NR5G_FR2_meas.std_insr_driver()
driver.ldir = 'DL'
driver.VSA_config()
print('calls:')
for c in mock_vsa.write.call_args_list:
    print(repr(c), c == call(':CONF:NR5G:DL:CC1:FRAM1:BWP0:ALL0:MOD Q1K'))
print('contains:', any(c == call(':CONF:NR5G:DL:CC1:FRAM1:BWP0:ALL0:MOD Q1K') for c in mock_vsa.write.call_args_list))
mock_bench.stop()
