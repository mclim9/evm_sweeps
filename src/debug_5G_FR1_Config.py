from helper.bench_config import bench
from driver.NR5G_FR1_vsa_fsw import VSA_driver
from driver.NR5G_FR1_vsg_smw import VSG_driver


if __name__ == '__main__':
    林 = bench()
    # 林.VSA = bench().VSA_start('fsw43-101238')
    林.VSA = bench().VSA_start('172.24.225.101')
    print(林.VSA.query('*IDN?'))
    錦 = VSA_driver(林.VSA)
    錦.freq = 7.4e9               # Center Frequency, Hz
    錦.scs  = 30                  # Sub Carr Spacing: 30; 60;
    錦.rb   = 1092                # number RB
    錦.rbo  = 0                   # RB Offset
    錦.bw   = 500                 # 10; 50; 100
    錦.vsa_configure()
    錦.vsa_set_frequency(7.4e9)
    林.VSA.clear_error()

    # 林.VSG = bench().VSG_start('smw200a-120297')
    林.VSG = bench().VSG_start('172.24.225.131')
    print(林.VSG.query('*IDN?'))
    暉 = VSG_driver(林.VSG)
    暉.freq = 7.4e9               # Center Frequency, Hz
    暉.scs  = 30                  # Sub Carr Spacing: 30; 60;
    暉.rb   = 1092                # number RB
    暉.rbo  = 0                   # RB Offset
    暉.bw   = 500                 # 10; 50; 100
    暉.pwr  = -10                 # VSG Initial power
    暉.vsg_configure()
    暉.vsg_set_frequency(7.4e9)
    林.VSG.clear_error()
'''
- Overview
    - 400 MHz CC
    - 491.52 MHz sample rate
    - TX carrier Frequency = 7.4 GHz
    - Num tx ant = 1
    - 30 ms duration
    - 30 kHz SCS
    - 1024 QAM Table
- DMRS
    Type 1
    TypeAPos=2
    2 DMRS symbols (add pos 1)
    Scr ID = 123 (N_SCID=0)
    - 1 layer (DMRS Antenna port=0), DMRS and data multiplexed
- PDSCH
    start symbol = 1, length=13
    Mapping Type A
    RA Type 1
    start RB=0
    num RB=1092
- MCS24
- PDSCH data Scr ID = 321

Some other basic assumptions (though this vector does not have PDCCH):
- 400 MHz BW = 1092 RBs (=273*4)
- Extend 38.212 Table 5.4.2.1-1 for n_prb_lbrm with 400 MHz BW value of 1092 (needed for rate matching to work)
- Extend Coreset bitmap definition to 182 bits to allow for PDCCH to be placed anywhere in the 400 MHz BW
- DCI 1_0 and 1_1 will need to have bigger sized fields for RIV
'''
