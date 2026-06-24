import os
import sys

# Add src directory to path for imports when running standalone
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from helper.bench_config import BenchConfig
def get_ch_power_init(vsa):
    curr_App = vsa.query(":INST:SEL?")              # Current App
    vsa.write(":INST:DEL 'ChPwr'")                  # Delete ch if exist
    vsa.write(":INST:CRE:NEW SANALYZER, 'ChPwr'")   # Create ch
    vsa.write(":SENS:WIND1:DET1:FUNC RMS")
    vsa.write(":SENS:SWE:TIME:AUTO OFF")
    vsa.write(":SENS:SWE:TIME 0.001")
    vsa.write(":CALC1:MARK1:STAT ON")
    vsa.write(":CALC1:MARK1:FUNC:BPOW:STAT ON")
    vsa.query(f":INST:SEL '{curr_App}';*OPC?")
    # vsa.clear_error()


def get_ch_power(vsa):                                  # K575 Mode
    curr_App = vsa.query(":INST:SEL?")                  # Current App
    curr_freq = vsa.query(":SENS1:FREQ:CENT?")
    vsa.query(f":INST:SEL 'ChPwr';*OPC?")
    vsa.write(f":SENS1:FREQ:CENT {curr_freq}")
    vsa.write(":SENS1:FREQ:SPAN 8e9")
    vsa.write(f":CALC1:MARK1:X {curr_freq}")            # Marker Freq
    vsa.write(":CALC1:MARK1:FUNC:BPOW:SPAN 8e9")        # Ch Bandwidth
    vsa.write(":INIT:CONT OFF")                         # Single Sweep
    vsa.query(":INIT:IMM;*OPC?")                        # Update screen
    chPwr = vsa.queryFloat(':CALC:MARK:FUNC:BPOW:RES?')
    vsa.query(f":INST:SEL '{curr_App}';*OPC?")
    # vsa.write(f":INST:SEL '{curr_App}';*OPC?")
    # vsa.clear_error()
    return chPwr

if __name__ == '__main__':
    bench = BenchConfig()
    vsa = bench.VSA_start()
    get_ch_power_init(vsa)
    get_ch_power(vsa)
