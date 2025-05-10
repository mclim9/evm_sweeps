from bench_config import bench
import numpy as np

class option_functions():
    def __init__(self):
        self.VSA = bench().VSA_start()
        self.VSA.s.settimeout(30)           # For AutoEVM
        self.VSG = bench().VSG_start()

    def VSA_Config(self):
        self.VSA.query('*RST;*OPC?')                                # Reset
        self.VSA.tick()
        # self.VSA.query(f':INST:CRE:NEW SAN, "Spectrum";*OPC?')      # Opens Spectrum Mode
        self.VSA.write(f':SENS:FREQ:CENT {frequncy}')               # Center Freq, Hz
        self.VSA.write(f':SENS:FREQ:SPAN 100e6')                    # Span, Hz
        self.STN_Noise_Marker()
        self.VSA.clear_error()

    def STN_Noise_Marker(self):
        self.VSA.write(f':SENS:WIND1:DET1:FUNC RMS')                # RMS Detector
        self.VSA.write(f':SENS:SWE:TIME:AUTO OFF')                  # Sweep time manual
        self.VSA.write(f':SENS:SWE:TIME {swp_time}')                # Sweep Time, sec
        self.VSA.write(f':CALC1:DELT1:FUNC:PNO:STAT OFF')           # PNO Off
        self.VSA.write(f':CALC1:MARK1:FUNC:NOIS:STAT ON')           # Marker1 Noise Marker
        self.VSA.write(f':CALC1:MARK1:X {frequncy}')                # Marker1 Noise Marker

    def get_VSA_sweep(self):
        self.VSA.tick()
        self.VSA.write('INIT:CONT OFF')                             # Cont Sweep off
        self.VSA.query('INIT:IMM;*OPC?')                            # Single Sweep
        marker1 = self.VSA.queryFloat(':CALC1:MARK1:Y?')            # Marker1 Y val
        swp_time = self.VSA.tock()
        return marker1, swp_time

if __name__ == '__main__':
    frequncy = 6e9
    swp_time = 1.00
    林 = option_functions()
    林.VSA_Config()
    meas = []
    for i in range(100):
        mkr1, testtime = 林.get_VSA_sweep()
        meas.append(mkr1)
        print(f'{frequncy}, {mkr1:.2f}dBm, {swp_time:.3f}sec, {testtime:.3f}sec')
    meas_arry = np.array(meas)
    avg = np.mean(meas_arry)        # Calc average
    min = np.min(meas_arry)         # Calc minimum
    max = np.max(meas_arry)         # Calc maximum
    std_dev = np.std(meas_arry)     # Calc standard deviation
    print(f'Min:{min:.3f} Max:{max:.3f} Avg:{avg:.3f} StdDev:{std_dev:.3f} Delta:{max - min:.3f}')
