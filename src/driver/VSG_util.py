import os
import sys

# Add src directory to path for imports when running standalone
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from helper.bench_config import BenchConfig

def set_SMW_K575(vsg, mode):                                # K575 Mode
    vsg.write(':SOUR1:CORR:OPT:RF:IQM 1')                   # Optimize IQ
    vsg.write(':SOUR1:CORR:OPT:RF:HEAD 1')                  # Optimize Headroom
    if 'OFF' in mode:
        vsg.write(':SOUR1:CORR:OPT:RF:LIN OFF')             # Linearization Mode  | OFF | AUTO | MAN
    elif 'ON' in mode:
        # meas.VSG.query(':SOUR1:CORR:OPT:RF:LIN:ADJ?')     # Linearize RF Button
        vsg.query(':SOUR1:CORR:OPT:RF:LIN AUTO;*OPC?')      # Linearization Mode  | OFF | AUTO | MAN
    vsg.query('*OPC?')


if __name__ == '__main__':
    bench = BenchConfig()
    vsg = bench.VSG_start()
    set_SMW_K575(vsg, 'OFF')
