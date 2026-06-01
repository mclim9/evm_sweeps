import os
from helper.utils import method_timer
from helper.bench_config import BenchConfig
from driver.base_vsg import VSGDriver

class VSG_driver(VSGDriver):
    def __init__(self, VSG=None):
        self.VSG = VSG or BenchConfig().VSG_start()
        self.bw = 5                                 # MHz
        self.rbc = 24                               # Num RB
        self.rbo = 0                                # RB Offset
        self.pwr = -10                              # Initial power dBm
        self.Wavename = 'default'

    @method_timer
    def vsg_configure(self):
        """VSG Config Before start of test suite"""
        self.VSG.write(':SOUR1:BB:EUTR:STDM LTE')                       # 4G Std
        self.VSG.write(':SOUR1:BB:EUTR:DUPL FDD')                       # Duplexing: FDD
        self.VSG.write(':SOUR1:BB:EUTR:LINK UP')                        # Link direction: UP
        self.VSG.write(f':SOUR1:BB:EUTR:UL:BW BW{self.bw}_00')          # Ch BW
        self.VSG.write(f':SOUR1:BB:EUTR:UL:CELL0:SUBF0:ALL0:PUSC:SET1:RBC {self.rbc}')
        self.VSG.write(f':SOUR1:BB:EUTR:UL:CELL0:SUBF0:ALL0:PUSC:SET1:VRB {self.rbo}')
        self.VSG.write(':SOUR1:BB:EUTR:UL:CELL0:SUBF0:ALL0:PUSC:MOD QAM256')
        self.VSG.write(':SOUR1:BB:EUTR:STAT 1')                         # BB State On
        self.VSG.query(f':SOUR1:POW:LEV:IMM:AMPL {self.pwr};*OPC?')     # Initial power

        self.VSG.write(':OUTP1:STAT 1')                                 # RF On
        self.VSG.query(':SOUR1:CORR:OPT:EVM 1;*OPC?')                   # Optimize EVM
        self.VSG.write(':SOUR1:BB:EUTR:TRIG:OUTP1:MODE REST')           # Marker Mode
        self.VSG.query('*OPC?')

    def vsg_get_extra(self) -> str:
        return "SMW-LTE"

    def vsg_save_state(self) -> None:
        """VSG Save State"""
        self.VSG.query('*IDN?')
        ldir = self.VSG.query(':SOUR1:BB:EUTR:LINK?')
        dupl = self.VSG.query(':SOUR1:BB:EUTR:DUPL?')

        # Normalize link direction for naming and SCPI path
        lpath = 'UL' if ldir == 'UP' else 'DL'

        mod  = self.VSG.query(f':SOUR1:BB:EUTR:{lpath}:CELL0:SUBF0:ALL0:PUSC:MOD?')
        rbn  = self.VSG.query(f':SOUR1:BB:EUTR:{lpath}:CELL0:SUBF0:ALL0:PUSC:SET1:RBC?')
        rbo  = self.VSG.query(f':SOUR1:BB:EUTR:{lpath}:CELL0:SUBF0:ALL0:PUSC:SET1:VRB?')
        chbw = self.VSG.query(f':SOUR1:BB:EUTR:{lpath}:BW?')

        self.Wavename = f'LTE_{lpath}_{dupl}_{chbw}_{rbn}RB_{rbo}rbo_{mod}'
        self.VSG.query(f':SOUR1:BB:EUTR:SETT:STOR "/var/user/{self.Wavename}";*OPC?')
        SMW_IP = self.VSG.s.getpeername()[0]
        os.system(f'start \\\\{SMW_IP}\\user')

    def vsg_set_frequency(self, freq: float) -> None:
        self.VSG.write(f':SOUR1:FREQ:CW {freq}')

    def vsg_set_power(self, pwr: float) -> None:
        self.VSG.write(f':SOUR1:POW:POW {pwr}')

if __name__ == '__main__':
    vsg = VSG_driver()
    vsg.vsg_configure()
    vsg.vsg_set_frequency(2.5e9)
    vsg.vsg_set_power(-15)
    print("VSG Configured for LTE")
