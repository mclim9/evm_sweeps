from helper.utils import method_timer
from helper.bench_config import BenchConfig
from driver.base_vsa import VSADriver
import os

class VSA_driver(VSADriver):
    def __init__(self, VSA=None):
        self.VSA = VSA or BenchConfig().VSA_start()
        self.VSA.s.settimeout(30)       # For AutoEVM
        self.freq = 6e9                 # Center Frequency, Hz
        self.scs  = 30                  # Sub Carr Spacing: 30; 60;
        self.rb   = 273                 # number RB
        self.rbo  = 0                   # RB Offset
        self.bw   = 100                 # 10; 50; 100
        self.pwr  = -10                 # VSG Initial power
        self.Wavename = 'default'       # Placeholder for VSA state filename

    def set_freq(self, freq):
        """Configures both VSG & VSA to frequency"""
        # self.VSA.write(f':CONF:NR5G:GMCF {freq}')                     # Ana CA Center Freq
        self.VSA.write(f':SENSE:FREQ:CENT {freq}')                      # Ana CC Center Freq
        self.VSG.write(f':SOUR1:FREQ:CW {freq}')                        # Generator center freq

    @method_timer
    def vsa_config(self):
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

    def vsa_extra(self):
        return 'none'

    @method_timer
    def vsa_get_ACLR(self):
        """Get VSA ACLR.

        Returns:
            tuple: (Channel Power(float), ACLR(float))
        """
        self.VSA.write(':CONF:NR5G:MEAS ACLR')
        self.vsa_sweep()
        chPwr = self.VSA.query(':CALC:MARK:FUNC:POW:RES? CPOW')         # Channel Power
        ACLRV = self.VSA.query(':CALC:MARK:FUNC:POW:RES? ACP')          # ACLR Relative
        print(f'{chPwr} {ACLRV}')
        return chPwr, ACLRV

    def vsa_get_attn_reflvl(self):
        """Get VSA input atten and ref level.

        Returns:
            tuple: (attenuation, reference_level)
        """
        attn = self.VSA.query('INP:ATT?')                               # Input Attn
        refl = self.VSA.queryFloat('DISP:TRAC:Y:SCAL:RLEV?')            # Ref Level
        return attn, refl

    def vsa_get_chPwr(self):
        """Get VSA channel power from result summary

        Returns:
            chPw(float): channel Power
        """
        chPw = self.VSA.queryFloat(':FETC:CC1:ISRC:FRAM:SUMM:POW?')     # VSA CW Ch Pwr
        return chPw

    @method_timer
    def vsa_get_EVM(self):
        """Takes a sweep then returns VSA EVM

        Returns:
            EVM(float) : EVM as defined by standard
        """
        try:
            self.vsa_sweep()                                            # Take a sweep
            EVM = self.VSA.queryFloat(':FETC:CC1:SUMM:EVM:ALL:AVER?')   # VSA CW
        except:                                                         # noqa
            print('EVM 2nd Try')
            self.vsa_sweep()                                            # Take a sweep
            EVM = self.VSA.queryFloat(':FETC:CC1:SUMM:EVM:ALL:AVER?')   # VSA CW
        return EVM

    def vsa_get_info(self):
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
    def vsa_level(self, method='LEV'):
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
            pwr = self.vsa_get_chPwr()
            self.VSA.write(f':DISP:WIND:TRAC:Y:SCAL:RLEV {pwr - 2}')    # Manually set ref level

    def vsa_load(self, file):
        """Load VSA demodulation state from file.

        Args:
            file (str): Path to state file.
        """
        self.VSA.write(f':MMEM:LOAD:DEM:C1 "{file}"')

    def vsa_save_state(self):
        """VSA Save 5G State"""
        self.VSA.query(f'*IDN?')
        self.VSA.query(f'MMEM:STOR:DEM "C:\\R_S\\instr\\{self.Wavename}.allocation";*OPC?')
        # HST_IP = self.VSA.s.getsockname()[0]                  # Host PC
        FSW_IP = self.VSA.s.getpeername()[0]                    # Instr
        os.system(f'start \\\\{FSW_IP}\\instr')

    @method_timer
    def vsa_sweep(self):
        """VSA take a single sweep"""
        self.VSA.write('INIT:CONT OFF')
        self.VSA.query('INIT:IMM;*OPC?')

if __name__ == '__main__':
    pass
