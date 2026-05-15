from helper.utils import method_timer, std_meas, std_config
from helper.bench_config import BenchConfig
from driver.base_vsg import VSGDriver
import os

class VSG_driver(VSGDriver):
    def __init__(self, VSG=None):
        """Initialize instrument connections and default parameters."""
        self.VSG = VSG or BenchConfig().VSG_start()
        self.freq = 6e9                 # Center Frequency, Hz
        self.scs  = 30                  # Sub Carr Spacing: 30; 60;
        self.rb   = 273                 # number RB
        self.rbo  = 0                   # RB Offset
        self.bw   = 100                 # 10; 50; 100
        self.pwr  = -10                 # VSG Initial power

    @method_timer
    def vsg_configure(self) -> None:
        """Config w/ VSG 5G Quick Settings"""
        self.VSG.write(f':SOUR1:BB:NR5G:LINK UP')               # Link Direction
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:DUPL FDD')     # FDD TDD
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:CARD FR1GT3')  # FR1GT3
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:CBW BW{self.bw}')      # BW50 BW100
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:SCSP SCS{self.scs}')   # Sub Carrier Spacing
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:ES:MOD QAM1024')# Modulation
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:ES:RBN {self.rb}')     # num RB
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:ES:RBOF {self.rbo}')   # RB Offset
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:APPL')             # QS Apply
        self.VSG.write(f':SOUR1:BB:NR5G:STAT 1')                # BB On

        # Additional Settings
        self.VSG.write(f':OUTP1:STAT 1')                        # RF On
        self.VSG.query(':SOUR1:CORR:OPT:EVM 1;*OPC?')           # Optimize EVM
        self.VSG.write(':SOUR1:BB:NR5G:TRIG:OUTP1:MODE REST')   # Maker Mode Arb Restart
        self.VSG.write(f':SOUR1:BB:NR5G:NODE:RFPH:MODE 0')      # Phase Compensation Off
        self.vsg_set_power(self.pwr)                            # Initial VSG power
        self.VSG.query('*OPC?')

    def vsg_set_frequency(self, freq: float) -> None:
        """Configures both VSG & VSA to frequency"""
        self.VSG.write(f':SOUR1:FREQ:CW {freq}')                        # Generator center freq

    def vsg_set_power(self, pwr: float) -> None:
        """Set VSG power (dBm)"""
        self.VSG.write(f':SOUR1:POW:POW {pwr}')                         # VSG Power

    def vsg_save_state(self):
        """VSG Save 5G State"""
        self.VSG.query(f'*IDN?')
        Band = self.VSG.query(':SOUR1:BB:NR5G:NODE:CELL0:CARD?')
        Dir  = self.VSG.query(':SOUR1:BB:NR5G:LINK?')
        BW   = self.VSG.query(':SOUR1:BB:NR5G:NODE:CELL0:CBW?')
        if Dir == 'UP':
            SCS  = self.VSG.query(':SOUR1:BB:NR5G:UBWP:USER0:CELL0:UL:BWP0:SCSP?')
            Mod  = self.VSG.query(':SOUR1:BB:NR5G:SCH:CELL0:SUBF0:USER0:BWP0:ALL0:MOD?')
            RBN  = self.VSG.query(':SOUR1:BB:NR5G:SCH:CELL0:SUBF0:USER0:BWP0:ALL0:RBN?')
            Dir  = 'UL'
        elif Dir == 'DOWN':
            SCS  = self.VSG.query(':SOUR1:BB:NR5G:UBWP:USER0:CELL0:DL:BWP0:SCSP?')
            Mod  = self.VSG.query(':SOUR1:BB:NR5G:SCH:CELL0:SUBF0:USER0:BWP0:ALL1:MOD?')
            RBN  = self.VSG.query(':SOUR1:BB:NR5G:SCH:CELL0:SUBF0:USER0:BWP0:ALL1:RBN?')
            Dir  = 'DL'

        self.Wavename = f'{Band}_{Dir}_{SCS}SCS_{BW}_{RBN}RB_{Mod}'
        self.VSG.query(f':SOUR1:BB:NR5G:SETT:STOR "/var/user/{self.Wavename}";*OPC?')
        # HST_IP = self.VSG.s.getsockname()[0]                          # Host PC
        SMW_IP = self.VSG.s.getpeername()[0]                            # Instr
        os.system(f'start \\\\{SMW_IP}\\user')

    def vsg_get_extra(self) -> str:
        return 'none'


if __name__ == '__main__':
    std_config(VSG_driver())
    std_meas(VSG_driver())
    instr = VSG_driver()
