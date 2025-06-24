from utils import method_timer
from bench_config import bench
import numpy as np

class option_functions():
    def __init__(self):
        self.VSA = bench().VSA_start()
        self.VSA.s.settimeout(30)                                   # For AutoEVM
        self.VSG = bench().VSG_start()

    @method_timer
    def VSA_Config(self):
        self.VSA.query('*RST;*OPC?')                                # Reset
        self.VSA.tick()
        # self.VSA.query(f':INST:CRE:NEW SAN, "Spectrum";*OPC?')    # Opens Spectrum Mode
        self.VSA.query(f':INST:SEL "Spectrum";*OPC?')               # Select Spectrum Mode
        self.VSA.write(f':SENS:FREQ:CENT {frequncy}')               # Center Freq, Hz
        self.VSA.write(f':SENS:FREQ:SPAN 100e6')                    # Span, Hz
        self.VSA.write(f':INP:GAIN:STAT ON')                        # pre-amp ON
        self.VSA.write(f':INP:GAIN:VAL 30')                         # pre-amp gain
        self.VSA.write(f':INP:ATT:AUTO OFF')                        # auto attenuation
        self.VSA.write(f':INP:ATT 0')                               # attenuation value
        self.VSA.write(f':DISP:WIND:TRAC:Y:SCAL:RLEV -40')          # Reference level
        self.STN_Noise_Marker()
        self.VSA.clear_error()

    def STN_Noise_Marker(self):
        self.VSA.write(f':SENS:WIND1:DET1:FUNC RMS')                # RMS Detector
        self.VSA.write(f':SENS:SWE:TIME:AUTO OFF')                  # Sweep time manual
        self.VSA.write(f':SENS:SWE:TIME {swp_time}')                # Sweep Time, sec
        self.VSA.write(f':CALC1:DELT1:FUNC:PNO:STAT OFF')           # PNO Off
        self.VSA.write(f':CALC1:MARK1:FUNC:NOIS:STAT ON')           # Marker1 Noise Marker
        self.VSA.write(f':CALC1:MARK1:X {frequncy}')                # Marker1 Noise Marker

    @method_timer
    def get_VSA_sweep_noise_mkr(self):
        self.VSA.write('INIT:CONT OFF')                             # Cont Sweep off
        self.VSA.query('INIT:IMM;*OPC?')                            # Single Sweep
        marker1 = self.VSA.queryFloat(':CALC:MARK1:Y?')             # Marker Y value
        marker1 = self.VSA.queryFloat(':CALC:MARK:FUNC:NOIS:RES?')  # Marker Nosie
        return marker1

    def get_Array_stats(self, in_arry):
        avg = np.mean(in_arry)        # Calc average
        min = np.min(in_arry)         # Calc minimum
        max = np.max(in_arry)         # Calc maximum
        std_dev = np.std(in_arry)     # Calc standard deviation
        out_str = f'Min:{min:.3f} Max:{max:.3f} Avg:{avg:.3f} StdDev:{std_dev:.3f} Delta:{max - min:.3f}'
        print(out_str)
        return out_str


if __name__ == '__main__':
    frequncy = 6e9
    swp_time = 1.00
    林 = option_functions()
    林.VSA_Config()
    meas = []
    print('Freqncy,   NoiseMkr,  CapTime, MeasTime')
    for i in range(10):
        mkr1, testtime = 林.get_VSA_sweep_noise_mkr()
        meas.append(mkr1)
        print(f'{frequncy / 1e9:7.3f}, {mkr1:.2f}dBm, {swp_time:.3f}sec, {testtime:.3f}sec')
    meas_arry = np.array(meas)
    林.get_Array_stats(meas_arry)
