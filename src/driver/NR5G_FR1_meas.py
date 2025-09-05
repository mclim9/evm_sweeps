from helper.utils import method_timer, std_meas, std_config
from helper.bench_config import bench
import os

class std_insr_driver():
    """FSx & SMx 5GNR FR1 driver"""

    def __init__(self):
        """Initialize instrument connections and default parameters."""
        self.VSA = bench().VSA_start()
        self.VSA.s.settimeout(30)       # For AutoEVM
        self.VSG = bench().VSG_start()
        self.freq = 6e9                 # Center Frequency, Hz
        self.scs  = 30                  # Sub Carr Spacing: 30; 60;
        self.rb   = 273                 # number RB
        self.rbo  = 0                   # RB Offset
        self.bw   = 100                 # 10; 50; 100
        self.pwr  = -10                 # VSG Initial power

    @method_timer
    def VSA_Config(self):
        """VSA Config Before start of test suite"""
        self.VSA.query('*RST;*OPC?')                            # Reset
        self.VSA.query(':SYST:DISP:UPD ON; *OPC?')              # Display on
        self.VSA.query(':INST:CRE:NEW NR5G, "5G NR"; *OPC?')    # Start 5GNR6
        self.VSA.write(':CONF:NR5G:LDIR UL')                    # Link Direction
        self.VSA.write(':CONF:NR5G:UL:CC1:TPR OFF')             # TPrecode
        self.VSA.write(':CONF:NR5G:UL:CC1:DFR MIDD')            # Band
        self.VSA.write(f':CONF:NR5G:UL:CC1:BW BW{self.bw}')     # BW
        self.VSA.write(f':CONF:NR5G:UL:CC1:FRAM1:BWP0:SSP SS{self.scs}') # SCS
        self.VSA.write(':CONF:NR5G:UL:CC1:FRAM1:BWP0:CSL 1')    # User Config Slot
        self.VSA.write(f':CONF:NR5G:UL:CC1:FRAM1:BWP0:RBC {self.rb}')   # BWP RB
        self.VSA.write(f':CONF:NR5G:UL:CC1:FRAM1:BWP0:RBOF {self.rbo}') # BWP RB Offset
        self.VSA.write(f':CONF:NR5G:UL:CC1:FRAM1:BWP0:SLOT0:ALL0:RBC {self.rb}')
        self.VSA.write(f':CONF:NR5G:UL:CC1:FRAM1:BWP0:SLOT0:ALL0:RBOF {self.rbo}')
        self.VSA.write(':CONF:NR5G:UL:CC1:FRAM1:BWP0:SLOT0:ALL0:MOD Q1K')

        # Additional Settings
        self.VSA.query(':LAY:ADD:WIND? "2",ABOV,EVSC')          # EVM vs Sym vs Carr
        self.VSA.write(':TRIG:SEQ:SOUR EXT')                    # Trigger External
        self.VSA.write(':SENS:NR5G:FRAM:COUN:AUTO OFF')         # Frame count off
        self.VSA.write(':SENS:NR5G:FRAM:COUN 1')                # Single frame
        self.VSA.write(':SENS:NR5G:FRAM:SLOT 1')                # Single Slot
        self.VSA.write(':UNIT:EVM DB')                          # EVM Units: DB PCT
        self.VSA.write(':SENS:SWE:TIME 0.0005')                 # Capture Time
        self.VSA.write(':CONF:NR5G:UL:CC1:RFUC:STAT OFF')       # Phase compensation

    @method_timer
    def VSA_get_ACLR(self):
        """Get VSA ACLR.

        Returns:
            tuple: (Channel Power(float), ACLR(float))
        """
        self.VSA.write(':CONF:NR5G:MEAS ACLR')
        self.VSA_sweep()
        chPwr = self.VSA.query(':CALC:MARK:FUNC:POW:RES? CPOW')         # Channel Power
        ACLRV = self.VSA.query(':CALC:MARK:FUNC:POW:RES? ACP')          # ACLR Relative
        print(f'{chPwr} {ACLRV}')
        return chPwr, ACLRV

    def VSA_get_attn_reflvl(self):
        """Get VSA input atten and ref level.

        Returns:
            tuple: (attenuation, reference_level)
        """
        attn = self.VSA.query('INP:ATT?')                               # Input Attn
        refl = self.VSA.queryFloat('DISP:TRAC:Y:SCAL:RLEV?')            # Ref Level
        return attn, refl

    def VSA_get_chPwr(self):
        """Get VSA channel power from result summary

        Returns:
            chPw(float): channel Power
        """
        chPw = self.VSA.queryFloat(':FETC:CC1:ISRC:FRAM:SUMM:POW?')     # VSA CW Ch Pwr
        return chPw

    @method_timer
    def VSA_get_EVM(self):
        """Takes a sweep then returns VSA EVM

        Returns:
            EVM(float) : EVM as defined by standard
        """
        try:
            self.VSA_sweep()                                            # Take a sweep
            EVM = self.VSA.queryFloat(':FETC:CC1:SUMM:EVM:ALL:AVER?')   # VSA CW
        except:                                                         # noqa
            print('EVM 2nd Try')
            self.VSA_sweep()                                            # Take a sweep
            EVM = self.VSA.queryFloat(':FETC:CC1:SUMM:EVM:ALL:AVER?')   # VSA CW
        return EVM

    def VSA_get_info(self):
        """VSA standard config detail string

        Returns:
            outStr(str): Formatted string with configuration details.
        """
        freq = self.VSA.query(':SENS:FREQ:CENT?')                       # Center Frequency
        freq = int(freq) / 1e9
        ldir = self.VSA.query(':CONF:NR5G:LDIR?')                       # LinkDir
        frng = self.VSA.query(f':CONF:{ldir}:DFR?')                     # Freq Range
        chbw = self.VSA.query(f':CONF:NR5G:{ldir}:CC1:BW?')             # Ch Width
        bscs = self.VSA.query(f':CONF:NR5G:{ldir}:CC1:FRAM1:BWP0:SSP?') # BWP Sub Carr Spacing
        bwrb = self.VSA.query(f':CONF:NR5G:{ldir}:CC1:FRAM1:BWP0:RBC?') # BWP RB Allocation
        cmod = self.VSA.query(f':CONF:NR5G:{ldir}:CC1:FRAM1:BWP0:SLOT0:ALL0:MOD?')    # channel Modulation
        if ldir == 'UL':
            tpre = self.VSA.query(f':CONF:NR5G:UL:CC1:TPR?')            # Trans Precoding State
        else:
            tpre = 'Off'
        phas = self.VSA.query(f':CONF:NR5G:{ldir}:CC1:RFUC:STAT?')      # Phase comp state
        time = self.VSA.query(':SENS:SWE:TIME?')                        # measure time
        nslt = self.VSA.query(':SENS:NR5G:FRAM:SLOT?')                  # number of slots

        outStr = f'{freq}GHz_{frng}_{ldir}_{chbw}_{bscs}_{bwrb}_{cmod}_TP{tpre}_PhaseComp{phas} {time}sec slots:{nslt}'
        print(outStr)
        return outStr

    @method_timer
    def VSA_level(self, method='LEV'):
        """Adjust VSA level settings.

        Args:
            method (str): 'LEV' for autolevel
                          'EVM' for autoEVM (if available)
                          'MAN' for manually set
        """
        if 'EVM' in method:
            self.VSA.query(f':SENS:ADJ:EVM;*OPC?')                      # AutoEVM
        elif 'LEV' in method:
            self.VSA.query(f':SENS:ADJ:LEV;*OPC?')                      # Autolevel
        else:
            self.VSA.write(f':INP:ATT:AUTO ON')                         # AutoAttenuation
            pwr = self.get_VSA_chPwr()
            self.VSA.write(f':DISP:WIND:TRAC:Y:SCAL:RLEV {pwr - 2}')    # Manually set ref level

    def VSA_Load(self, file):
        """Load VSA demodulation state from file.

        Args:
            file (str): Path to state file.
        """
        self.VSA.write(f':MMEM:LOAD:DEM:C1 "{file}"')

    def VSA_save_state(self):
        """VSA Save 5G State"""
        self.VSA.query(f'*IDN?')
        self.VSA.query(f'MMEM:STOR:DEM "C:\\R_S\\instr\\{self.Wavename}.allocation";*OPC?')
        # HST_IP = self.VSA.s.getsockname()[0]                  # Host PC
        FSW_IP = self.VSA.s.getpeername()[0]                    # Instr
        os.system(f'start \\\\{FSW_IP}\\instr')

    @method_timer
    def VSA_sweep(self):
        """VSA take a single sweep"""
        self.VSA.write('INIT:CONT OFF')
        self.VSA.query('INIT:IMM;*OPC?')

    @method_timer
    def VSG_Config(self):
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
        self.VSG.write(':SOUR1:BB:NR5G:NODE:RFPH:MODE 0')       # Phase Compensation Off
        self.VSG_pwr(self.pwr)                                  # Initial VSG power
        self.VSG.query('*OPC?')

    def VSG_pwr(self, pwr):
        """Set VSG power (dBm)"""
        self.VSG.write(f':SOUR1:POW:POW {pwr}')                         # VSG Power

    def VSG_save_state(self):
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

    def VSx_freq(self, freq):
        """Configures both VSG & VSA to frequency"""
        # self.VSA.write(f':CONF:NR5G:GMCF {freq}')                     # Ana CA Center Freq
        self.VSA.write(f':SENSE:FREQ:CENT {freq}')                      # Ana CC Center Freq
        self.VSG.write(f':SOUR1:FREQ:CW {freq}')                        # Generator center freq


if __name__ == '__main__':
    # std_config(std_insr_driver())
    # std_meas(std_insr_driver())
    instr = std_insr_driver()
    instr.VSA_get_ACLR()
