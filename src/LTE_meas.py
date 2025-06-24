from utils import method_timer, std_meas, std_config
from bench_config import bench
import os

class std_insr_driver():
    """FSx & SMx LTE driver"""

    def __init__(self):
        """Initialize instrument connections and default parameters."""
        self.VSA = bench().VSA_start()
        self.VSA.s.settimeout(30)       # For AutoEVM
        self.VSG = bench().VSG_start()
        self.rbc = 24                   # Num RB
        self.rbo = 0                    # RB Offset
        self.bw  = 5                    # Ch BW, MHz 3; 5; 10; 15; 20
        self.freq = 6e9                 # Center Frequency, Hz
        self.pwr  = -10                 # VSG Initial power

    @method_timer
    def VSA_Config(self):
        """VSA Config Before start of test suite"""
        self.VSA.query('*RST;*OPC?')                                    # Reset
        self.VSA.query(f':INST:CRE:NEW LTE, "LTE";*OPC?')               # Opens LTE Mode
        self.VSA.write(f':TRIG:SEQ:SOUR EXT;*WAI')                      # Trigger: IMM|EXT|EXT2|RFP|IFP|TIME|VID|BBP|PSEN
        self.VSA.write(f':INIT:CONT ON;*WAI')                           # Continuous sweep: ON|OFF
        self.VSA.write(f':CONF:LTE:DUPL FDD;*WAI')                      # Duplexing:  FDD|TDD
        self.VSA.write(f':CONF:LTE:LDIR UL;*WAI')                       # Link direction: UL|DL
        self.VSA.write(f':CONF:LTE:UL:CC:BW BW{self.bw}_00;*WAI')       # Channel BW: BW1_40|BW3_00|BW5_00|BW10_00|BW15_00|BW20_00
        self.VSA.write(f':CONF:LTE:UL:CC:SUBF0:ALL:CLUS1:RBC {self.rbc}')    # Num RB: 0 to 100
        self.VSA.write(f':CONF:LTE:UL:CC:SUBF0:ALL:CLUS1:rboF {self.rbo}')   # RB Offset: 0 to 99
        self.VSA.write(f':CONF:LTE:UL:CC:SUBF0:ALL:MOD QAM256')         # Modulation
        self.VSA.write(f':SENS:SWE:TIME 0.00201;*WAI')                  # Sweep Time: Range: 0.00201s to 0.0501
        # self.VSA.write(':SENS:LTE:FRAM:COUN:AUTO OFF')                # Frame count off
        # self.VSA.write(':SENS:LTE:FRAM:COUN 1')                       # Single frame
        # self.VSA.write(':SENS:SWE:TIME 0.002')                        # Capture Time
        self.VSA.write(f':SENS:LTE:FRAM:SSUB ON;*WAI')                  # Single SUbframe Mode: ON|OFF
        # self.VSA.query(f':SENS:ADJ:LEV;*OPC?')                        # Auto Level

        # Non Std Specific Settings
        self.VSA.write(f':SYST:DISP:UPD ON')                            # Turns on VSA display: ON|OFF
        self.VSA.write('INIT:CONT OFF')                                 # Single Sweep
        self.VSA.query(f':INIT:IMM;*OPC?')                              # Run Single
        self.VSA.write(':TRIG:SEQ:SOUR EXT')                            # Trigger External

    @method_timer
    def VSA_get_ACLR(self):
        """Get VSA ACLR.

        Returns:
            tuple: (Channel Power(float), ACLR(float))
        """
        self.VSA.write(':CONF:LTE:MEAS ACLR')
        self.VSA_sweep()
        chPwr = self.VSA.queryFloat(':CALC:MARK:FUNC:POW:RES? CPOW')         # Channel Power
        ACLRV = self.VSA.queryFloat(':CALC:MARK:FUNC:POW:RES? ACP')          # ACLR Relative
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
        """Get VSA Channel Power

        Returns:
            chPw(float) : Channel Power
        """
        chPw = self.VSA.queryFloat(':FETC:CC1:SUMM:POW:AVER?')          # VSA CW Ch Pwr
        return chPw

    @method_timer
    def VSA_get_EVM(self):
        """Takes a sweep then returns VSA EVM

        Returns:
            EVM(float) : EVM as defined by standard
        """
        try:
            self.VSA.query('INIT:IMM;*OPC?')                            # Take a sweep
            EVM = self.VSA.queryFloat(':FETC:CC1:SUMM:EVM:ALL:AVER?')   # VSA CW
        except:                                                         # noqa
            self.VSA.query('INIT:IMM;*OPC?')                            # Take a sweep
            EVM = self.VSA.queryFloat(':FETC:CC1:SUMM:EVM:ALL:AVER?')   # VSA CW
        return EVM

    @method_timer
    def VSA_get_info(self):
        """VSA standard config detail string

        Returns:
            outStr(str): Formatted string with configuration details.
        """
        freq = self.VSA.query(':SENS:FREQ:CENT?')                       # Center Frequency
        freq = int(freq) / 1e9
        ldir = self.VSA.query(':CONF:LTE:LDIR?')                        # link direction
        dupl = self.VSA.query(':CONF:LTE:DUPL?')                        # duplex mode
        ldir = "UL" if ldir == "UL" else "DL"
        chbw = self.VSA.query(f':CONF:LTE:{ldir}:CC:BW?')
        cmod = self.VSA.query(f':CONF:LTE:{ldir}:CC:SUBF0:ALL:MOD?')
        rbn  = self.VSA.query(f':CONF:LTE:{ldir}:CC:SUBF0:ALL:CLUS1:RBC?')
        rbo  = self.VSA.query(f':CONF:LTE:{ldir}:CC:SUBF0:ALL:CLUS1:RBOF?')
        # time = self.VSA.query(':SENS:SWE:TIME?')                      # measure time
        time = 0

        outStr = f'{freq:.3f}GHz_{ldir}_{dupl}_{chbw}_15kHz_{rbn}RB_{rbo}RBO_{cmod} {time}sec'
        print(outStr)
        return outStr

    @method_timer
    def VSA_level(self, method):
        """Adjust VSA level settings.

        Args:
            method (str): 'LEV' for autolevel
                          'EVM' for autoEVM (if available)
                          'MAN' for manually set
        """
        if 'LEV' in method:
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
        """VSA Save LTE State"""
        self.VSA.query(f'*IDN?')

        ldir = self.VSA.query(':CONF:LTE:LDIR?')                        # link direction
        dupl = self.VSA.query(':CONF:LTE:DUPL?')                        # duplex mode
        ldir = "UL" if ldir == "UL" else "DL"
        chbw = self.VSA.query(f':CONF:LTE:{ldir}:CC:BW?')
        rbn  = self.VSA.query(f':CONF:LTE:{ldir}:CC:SUBF0:ALL:CLUS1:RBC?')
        rbo  = self.VSA.query(f':CONF:LTE:{ldir}:CC:SUBF0:ALL:CLUS1:rboF?')
        cmod = self.VSA.query(f':CONF:LTE:{ldir}:CC:SUBF0:ALL:MOD?')

        self.Wavename = f'LTE_{ldir}_{dupl}_{chbw}_{rbn}RB_{rbo}rbo_{cmod}'
        self.VSA.query(f'MMEM:STOR:CC:DEM "C:\\R_S\\instr\\{self.Wavename}.allocation";*OPC?')
        FSW_IP = self.VSA.s.getpeername()[0]            # Instr
        os.system(f'start \\\\{FSW_IP}\\instr')

    @method_timer
    def VSA_sweep(self):
        """VSA take a single sweep"""
        self.VSA.write('INIT:CONT OFF')                                 # Cont Sweep off
        self.VSA.query('INIT:IMM;*OPC?')                                # Single Sweep

    @method_timer
    def VSG_Config(self):
        """VSG Config Before start of test suite"""
        self.VSG.write(f':SOUR1:BB:EUTR:STDM LTE')                      # 4G Std: LTE|EUTRA|IOT
        self.VSG.write(f':SOUR1:BB:EUTR:DUPL FDD')                      # Duplexing: FDD|TDD
        self.VSG.write(f':SOUR1:BB:EUTR:LINK UP')                       # Link direction: UP|DOWN
        self.VSG.write(f':SOUR1:BB:EUTR:UL:BW BW{self.bw}_00')          # Ch BW: BW1_40|BW3_00|BW5_00|BW10_00|BW15_00|BW20_00|BW0_20|USER
        self.VSG.write(f':SOUR1:BB:EUTR:UL:CELL0:SUBF0:ALL0:PUSC:SET1:RBC {self.rbc}')   # Num of RBs: Range: 0 to 110
        self.VSG.write(f':SOUR1:BB:EUTR:UL:CELL0:SUBF0:ALL0:PUSC:SET1:VRB {self.rbo}')   # RB Offset: Range 0 to 49
        self.VSG.write(f':SOUR1:BB:EUTR:UL:CELL0:SUBF0:ALL0:PUSC:MOD QAM256')   # RB Offset: Range 0 to 49
        self.VSG.write(f':SOUR1:BB:EUTR:STAT 1')                        # BB State: 0|1
        self.VSG.query(f':SOUR1:POW:LEV:IMM:AMPL -10;*OPC?')            # CW power: Range:-130 - +30dBm

        # Non Std Specific Settings
        self.VSG.write(f':OUTP1:STAT 1')                                # RF On
        self.VSG.query(':SOUR1:CORR:OPT:EVM 1;*OPC?')                   # Optimize EVM
        self.VSG.write(':SOUR1:BB:EUTR:TRIG:OUTP1:MODE REST')           # Maker Mode Arb Restart
        self.VSG_pwr(self.pwr)                                          # Initial VSG power
        self.VSG.query('*OPC?')

    def VSG_pwr(self, pwr):
        self.VSG.write(f':SOUR1:POW:POW {pwr}')                         # VSG Power

    def VSG_save_state(self):
        """VSG Save State"""
        self.VSG.query(f'*IDN?')
        ldir = self.VSG.query(':SOUR1:BB:EUTR:LINK?')
        dupl = self.VSG.query(':SOUR1:BB:EUTR:DUPL?')
        if ldir == 'UP':
            ldir  = 'UL'
            Mod  = self.VSG.query(f':SOUR1:BB:EUTR:{ldir}:CELL0:SUBF0:ALL0:PUSC:MOD?')
            rbn  = self.VSG.query(f':SOUR1:BB:EUTR:{ldir}:CELL0:SUBF0:ALL0:PUSC:SET1:RBC?')
            rbo  = self.VSG.query(f':SOUR1:BB:EUTR:{ldir}:CELL0:SUBF0:ALL0:PUSC:SET1:VRB?')
            chbw = self.VSG.query(f':SOUR1:BB:EUTR:{ldir}:BW?')
        elif ldir == 'DOWN':
            ldir  = 'DL'
            Mod  = self.VSG.query(f':SOUR1:BB:EUTR:{ldir}:CELL0:SUBF0:ALL0:PUSC:MOD?')
            rbn  = self.VSG.query(f':SOUR1:BB:EUTR:{ldir}:CELL0:SUBF0:ALL0:PUSC:SET1:RBC?')
            rbo  = self.VSG.query(f':SOUR1:BB:EUTR:{ldir}:CELL0:SUBF0:ALL0:PUSC:SET1:VRB?')
            chbw = self.VSG.query(f':SOUR1:BB:EUTR:{ldir}:BW?')
        self.Wavename = f'LTE_{ldir}_{dupl}_{chbw}_{rbn}RB_{rbo}rbo_{Mod}'
        self.VSG.query(f':SOUR1:BB:EUTR:SETT:STOR "/var/user/{self.Wavename}";*OPC?')
        SMW_IP = self.VSG.s.getpeername()[0]        # Instr
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
    # LTE_FDD_5MHz_QPSK_1RB_0StartRB_SCS15kHz
    # LTE_FDD_5MHz_QPSK_1RB_24StartRB_SCS15kHz
    # 2.5GHz; QPSK; FDD
