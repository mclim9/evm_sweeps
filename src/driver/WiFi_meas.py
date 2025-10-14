try:
    from helper.utils import method_timer, std_meas, std_config
    from helper.bench_config import bench
except ImportError:
    from ..helper.utils import method_timer, std_meas, std_config
    from ..helper.bench_config import bench
import os


class std_insr_driver():
    """FSx & SMx 802.11 driver"""

    def __init__(self):
        """Initialize instrument connections and default parameters."""
        self.VSA = bench().VSA_start()
        self.VSA.s.settimeout(30)                               # For AutoEVM
        self.VSG = bench().VSG_start()
        self.pwr  = -10                                         # VSG Initial power

    @method_timer
    def VSA_config(self):
        """VSA Config Before start of test suite"""
        self.VSA.query('*RST;*OPC?')                            # Reset
        self.VSA.query(':SYST:DISP:UPD ON; *OPC?')              # Display on
        self.VSA.query(':INST:CRE:NEW WLAN, "WLAN"; *OPC?')     # Start 5GNR6
        self.VSA.write(':INIT:CONT ON')                         # Single Sweep
        self.VSA.write(':CONF:STAN 11')                         # 11:be
        self.VSA.write(':SENS:SWE:TIME 0.002')                  # Sweep Time
        self.VSA.write(':SENS:DEM:TXAR OFF')                    # Burst Search
        self.VSA.write(':SENS:DEM:CEST 0')                      # ChEst 1:Payload 0:Pre Only
        # self.VSA.write(':SENS:DEM:CEST:PAYL 0')               # ChEst Payload
        # self.VSA.write(':SENS:DEM:CEST:RANG PRE2T')           # ChEst PRE1T(Preamble) PRE1T(Data)
        self.VSA.write(':SENS:DEM:INT:WIEN:DSPR:STAT MANUAL')   # Wiener Filter
        self.VSA.write(':SENS:DEM:INT:WIEN:DSPR 3.00')          # Wiener Filter
        # self.VSA.write(':SENS:BAND:CHAN:AUTO:TYPE MB320')     # Meas 320MHz
        # self.VSA.write('CONF:WLAN:RUC:SEGM1:CHAN1:RUL1:USER1:MCS 13')

        # self.VSA.write(':LAY:REPL:WIND "3",RSDetailed')         # Detailed Result Summary

    def VSA_extra(self):
        extra = ''
        if extra == 'IQNC':
            self.VSA.query(':SENS:ADJ:NCAN:AVER:STAT ON; *OPC?')            # IQNC On
            self.VSA.write(':SENS:ADJ:NCAN:AVER:COUN 10')                   # IQNC Averaging
        return extra

    @method_timer
    def VSA_get_ACLR(self):
        """Get VSA ACLR.

        Returns:
            tuple: (Channel Power(float), ACLR(float))
        """
        pass

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
        chPw = 999
        # chPw = self.VSA.queryFloat(':FETC:CC1:ISRC:FRAM:SUMM:POW?')   # VSA CW Ch Pwr
        return chPw

    @method_timer
    def VSA_get_EVM(self):
        """Takes a sweep then returns VSA EVM

        Returns:
            EVM(float) : EVM as defined by standard
        """
        self.VSA_sweep()
        EVM = self.VSA.query(':FETC:BURS:EVM:DATA:AVER?').split(',')    # EVM
        try:
            EVM = float(EVM[0])
        except:                                                         # noqa
            EVM = 999
        return EVM

    def VSA_get_info(self):
        """VSA standard config detail string

        Returns:
            outStr(str): Formatted string with configuration details.
        """
        freq = self.VSG.query(':SOUR1:FREQ:CW?')                        # Center Frequency
        freq = int(freq) / 1e9
        Std  = self.VSG.query(':SOUR1:BB:WLNN:FBL1:TMOD?')              # Standard
        BW   = self.VSG.query(':SOUR1:BB:WLNN:BW?')                     # Bandwidth
        MCS  = self.VSG.query(':SOUR1:BB:WLNN:FBL1:USER1:MCS?')         # MCS
        Data = self.VSG.query(':SOUR1:BB:WLNN:FBL1:USER1:DATA:LENG?')   # PPDU Length
        outStr = f'{freq}GHz_{Std}_{BW}_{MCS}_{Data}A-MPDU'
        print(outStr)
        return outStr

    @method_timer
    def VSA_level(self, method):
        """Adjust VSA level settings.

        Args:
            method (str): 'LEV' for autolevel
                          'EVM' for autoEVM (not available)
                          'MAN' for manually set
        """
        if 'LEV' in method:
            self.VSA.query(f':CONF:POW:AUTO ONCE;*OPC?')                # AutoLevel
        elif 'EVM' in method:
            self.VSA.query(f':CONF:POW:AUTO ONCE;*OPC?')                # AutoLevel
        else:
            self.VSA.write(f':INP:ATT:AUTO ON')                         # AutoAttenuation
            pwr = self.get_VSA_chPwr()
            self.VSA.write(f':DISP:WIND:TRAC:Y:SCAL:RLEV {pwr - 2}')    # Manually set ref level

    def VSA_load(self, file):
        """Load VSA demodulation state from file.

        Args:
            file (str): Path to state file.
        """
        self.VSA.write(f':MMEM:LOAD:DEM:C1 "{file}"')

    def VSA_save_state(self):
        """VSA Save State"""
        self.VSA.query(f'*IDN?')
        # BW   = self.VSA.query(':SENS:BAND:CHAN:AUTO:TYPE?')
        BW   = self.VSA.queryInt(':TRAC:IQ:SRAT?') / 1e6
        PCKT = self.VSA.query(':FETC:BURS:PPDU:TYPE?')
        Dir  = self.VSA.query(':CONF:WLAN:RUC:EHTP?')
        Mod  = self.VSA.query(':CONF:WLAN:RUC:SEGM1:CHAN1:RUL1:USER1:MCS?')
        RUS  = self.VSA.query(':CONF:WLAN:RUC:SEGM1:CHAN1:RUL1:RUS?')
        # Pwr  = self.VSA.query(':FETC:BURS:PAYL?')
        # EVM  = self.VSA.query(':FETC:BURS:EVM:ALL:AVER?')
        if Dir == 'MU':
            Dir = 'Down'
        else:
            Dir = 'Up'
        self.Wavename = f'WiFi{BW}_{PCKT}_{Dir}_{RUS}_MCS{Mod}'
        self.VSA.query(f':MMEM:STOR:STAT 1,"C:\\R_S\\instr\\{self.Wavename}.dfl";*OPC?')
        FSW_IP = self.VSA.s.getpeername()[0]                    # Instr
        os.system(f'start \\\\{FSW_IP}')

    @method_timer
    def VSA_sweep(self):
        """VSA take a single sweep"""
        self.VSA.write('INIT:CONT OFF')                                 # Cont Sweep off
        self.VSA.query('INIT:IMM;*OPC?')                                # Single Sweep

    @method_timer
    def VSG_config(self):
        """Config w/ SMx before test suite"""
        self.VSG.write(f':SOUR1:BB:WLNN:BW BW320')                      # 320MHz BW
        self.VSG.write(f':SOUR1:BB:WLNN:FBL1:TMOD EHT320')              # Tx Mode
        self.VSG.write(f':SOUR1:BB:WLNN:FBL1:USER1:MCS MCS13')          # MCS
        self.VSG.write(f':SOUR1:BB:WLNN:FBL1:USER1:RUTY RU4996')        # RU Config
        self.VSG.write(f':SOUR1:BB:WLNN:FBL1:USER1:MPDU1:COUN 50')      # Num MPDU
        self.VSG.write(f':SOUR1:BB:WLNN:FBL1:GUAR GD08')                # Guard Duration
        self.VSG.write(f':SOUR1:BB:WLNN:FBL1:SYMD SD64')                # Symbol Duration
        self.VSG.write(f':SOUR1:BB:WLNN:FBL1:ITIM 0')                   # Idle Time
        self.VSG.write(f':SOUR1:BB:WLNN:CLIP:SPPS 1')                   # Signal Field Clipping
        self.VSG.write(f':SOUR1:BB:WLNN:STAT 1')                        # BB On

        # Additional Settings
        self.VSG.write(f':OUTP1:STAT 1')                                # RF On
        self.VSG.query(':SOUR1:CORR:OPT:EVM 1;*OPC?')                   # Optimize EVM
        self.VSG.write(':SOUR1:BB:WLNN:TRIG:OUTP1:MODE REST')           # Maker Mode Arb Restart
        self.VSG_pwr(self.pwr)                                          # Initial VSG power
        self.VSG.query('*OPC?')

    def VSG_extra(self):
        return 'none'

    def VSG_pwr(self, pwr):
        """Set VSG power (dBm)"""
        self.VSG.write(f':SOUR1:POW:POW {pwr}')                         # VSG Power

    def VSG_save_state(self):
        """VSG Save 802.11 State"""
        self.VSG.query(f'*IDN?')
        BW   = self.VSG.query(':SOUR1:BB:WLNN:BW?')
        PCKT = self.VSG.query(':SOUR1:BB:WLNN:FBL1:TMOD?')
        Dir  = self.VSG.query(':SOUR1:BB:WLNN:FBL1:LINK?')
        Mod  = self.VSG.query(':SOUR1:BB:WLNN:FBL1:USER1:MCS?')
        RUS  = self.VSG.query(':SOUR1:BB:WLNN:FBL1:USER1:RUTY?')

        self.Wavename = f'WiFi{BW}_{PCKT}_{Dir}_{RUS}_{Mod}'
        self.VSG.query(f':SOUR1:BB:WLNN:SETT:STOR "/var/user/{self.Wavename}";*OPC?')
        SMW_IP = self.VSG.s.getpeername()[0]        # Instr
        os.system(f'start \\\\{SMW_IP}\\user')

    def VSx_freq(self, freq):
        """Configures both VSG & VSA to frequency"""
        # self.VSA.write(f':CONF:NR5G:GMCF {freq}')                     # Ana CA Center Freq
        self.VSA.write(f':SENSE:FREQ:CENT {freq}')                      # Ana CC Center Freq
        self.VSG.write(f':SOUR1:FREQ:CW {freq}')                        # Generator center freq


if __name__ == '__main__':
    std_config(std_insr_driver())
    std_meas(std_insr_driver())
