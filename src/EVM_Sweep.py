from NR5G_meas import option_functions                      # protocol to use
# from WiFi_meas import option_functions                      # protocol to use
from bench_config import bench
import datetime
import timeit

class EVM_Sweep():
    def __init__(self):
        # Freq Sweep
        # self.mode_arry = ['ON','OFF']                     # SMW-K575
        # self.freq_arry = range(int(600e6), int(43e9), int(100e6))
        # self.pwr_arry = [-10]
        # self.lvl_arry = ['LEV']                           # LEV:autolevel EVM:autoEVM

        # Pwr Sweep
        self.mode_arry = ['OFF']                            # SMW-K575
        # self.freq_arry = [int(0.850e9), int(1.850e9), int(3.5e9), int(5.0e9), int(5.9e9), int(5.9e9)]
        self.freq_arry = range(int(1e9), int(50e9), int(1000e6))
        self.pwr_arry = range(-45, 15, 1)
        self.lvl_arry = ['LEV']                             # LEV:autolevel EVM:autoEVM

        self.VSA = bench().VSA_start()
        self.VSG = bench().VSG_start()
        self.startTime = datetime.datetime.now().strftime("%Y.%m.%d-%H%M%S")
        self.numb_iter = len(self.mode_arry) * len(self.freq_arry) * len(self.pwr_arry) * len(self.lvl_arry)
        self.curr_iter = 0
        self.time_start = timeit.default_timer()

    def calc_testtime(self):
        time_till_now = timeit.default_timer() - self.time_start
        time_left = time_till_now / (self.curr_iter + 1) * (self.numb_iter - self.curr_iter)
        time_done = datetime.datetime.now() + datetime.timedelta(seconds=time_left)
        time_dStr = time_done.strftime("%Y.%m.%d %H:%M:%S")
        print(f' |{self.curr_iter:3d} / {self.numb_iter} Done@:{time_dStr} {time_left / 60:6.2f}min left ')
        self.curr_iter += 1

    def file_write(self, outString, endStr='\n'):
        filename = f'{__file__.split(".py")[0]}_{self.startTime}.txt'
        fily = open(filename, '+a')
        fily.write(f'{outString}\n')
        print(outString, end=endStr)
        fily.close()

    def set_mode(self, mode):                                   # K575 Mode
        meas.VSG.write(':SOUR1:CORR:OPT:RF:IQM 1')              # Optimize IQ
        meas.VSG.write(':SOUR1:CORR:OPT:RF:HEAD 1')             # Optimize Headroom
        if 'OFF' in mode:
            meas.VSG.write(':SOUR1:CORR:OPT:RF:LIN OFF')        # Linearization Mode  | OFF | AUTO | MAN
        elif 'ON' in mode:
            # meas.VSG.query(':SOUR1:CORR:OPT:RF:LIN:ADJ?')     # Linearize RF Button
            meas.VSG.query(':SOUR1:CORR:OPT:RF:LIN AUTO;*OPC?') # Linearization Mode  | OFF | AUTO | MAN
        meas.VSG.query('*OPC?')

    def main(self):
        self.file_write(self.VSA.idn)
        self.file_write(self.VSG.idn)
        self.file_write(meas.get_info())
        self.file_write('Date,Time,K575,Freq,Power [dBm],RefLvl [dBm],Attn[dB],ChPwr[dBm],EVM[dB],Leveling,IQNC,Time[Sec]')
        meas.set_VSA_init()
        meas.set_VSG_init()
        for mode in self.mode_arry:
            self.set_mode(mode)
            self.set_mode(mode)
            for lvling in self.lvl_arry:
                for freq in self.freq_arry:
                    meas.set_freq(freq)
                    for pwr in self.pwr_arry:
                        self.VSG.write(f':SOUR1:POW:POW {pwr}')             # VSG Power
                        meas.set_VSA_level(lvling)
                        self.VSA.write('INIT:CONT OFF')
                        self.VSA.tick()
                        self.VSA.query('INIT:IMM;*OPC?')
                        endT = self.VSA.tock()
                        EVM = meas.get_EVM()
                        attn = self.VSA.query('INP:ATT?')                   # Input Attn
                        refl = self.VSA.queryFloat('DISP:TRAC:Y:SCAL:RLEV?')
                        chPw = meas.get_VSA_chPwr()
                        iqnc = 0
                        time = datetime.datetime.now().strftime("%Y/%m/%d,%H:%M:%S")
                        data = f'{time},{mode},{freq:11},{pwr:3d},{refl:6.2f},{attn:2s},{chPw:6.2f},{EVM:6.2f},{lvling},{iqnc},{endT:6.4f}'
                        self.file_write(data, endStr='')
                        self.calc_testtime()


if __name__ == '__main__':
    test_sweep = EVM_Sweep()
    meas = option_functions()
    test_sweep.main()
    # test_sweep.set_mode('ON')
    # meas.VSG.query('*IDN?')
