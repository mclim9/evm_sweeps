
def set_SMW_K575(self, mode):                                   # K575 Mode
    meas.VSG.write(':SOUR1:CORR:OPT:RF:IQM 1')              # Optimize IQ
    meas.VSG.write(':SOUR1:CORR:OPT:RF:HEAD 1')             # Optimize Headroom
    if 'OFF' in mode:
        meas.VSG.write(':SOUR1:CORR:OPT:RF:LIN OFF')        # Linearization Mode  | OFF | AUTO | MAN
    elif 'ON' in mode:
        # meas.VSG.query(':SOUR1:CORR:OPT:RF:LIN:ADJ?')     # Linearize RF Button
        meas.VSG.query(':SOUR1:CORR:OPT:RF:LIN AUTO;*OPC?') # Linearization Mode  | OFF | AUTO | MAN
    meas.VSG.query('*OPC?')


if __name__ == '__main__':
    test_sweep = EVM_Sweep()
    meas = option_functions()
    test_sweep.main()
    # test_sweep.set_mode('ON')
    # meas.VSG.query('*IDN?')
