from NR5G_FR1_meas import std_insr_driver                   # protocol to use
# from driver.LTE_meas import std_insr_driver                      # protocol to use
# from driver.WiFi_meas import std_insr_driver                     # protocol to use
from bench_config import bench
import datetime
import timeit

class EVM_Sweep():
    def __init__(self):
        # self.freq_arry = [int(0.850e9), int(1.850e9), int(3.5e9), int(5.0e9), int(5.9e9), int(5.9e9)]
        # self.freq_arry = range(int(1e9), int(50e9), int(1000e6))
        self.freq_arry = [int(0.850e9)]
        self.pwr_arry = range(-45, 15, 1)
        self.lvl_arry = ['LEV']                                     # LEV:autolevel EVM:autoEVM

        self.VSA = bench().VSA_start()
        self.VSG = bench().VSG_start()
        self.startTime = datetime.datetime.now().strftime("%Y.%m.%d-%H%M%S")
        self.numb_iter = len(self.freq_arry) * len(self.pwr_arry) * len(self.lvl_arry)
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

    def main(self):
        self.file_write(self.VSA.idn)
        self.file_write(self.VSG.idn)
        meas.VSA_Config()
        meas.VSG_Config()
        self.file_write(meas.VSA_get_info())
        self.file_write('Date,Time,Freq,Power [dBm],RefLvl [dBm],Attn[dB],ChPwr[dBm],EVM[dB],Leveling,AL-Time,Time[Sec],TotalTime[Sec]')
        for lvling in self.lvl_arry:
            for freq in self.freq_arry:
                meas.VSx_freq(freq)
                for pwr in self.pwr_arry:
                    meas.VSG_pwr(pwr)                       # Set VSG Power
                    alT = meas.VSA_level(lvling)[1]         # Get VSA leveling time(-float-)
                    EVM, evmT  = meas.VSA_get_EVM()         # Get EVM(-float-) & EVM Time(-float-)
                    attn, refl = meas.VSA_get_attn_reflvl() # Get Attn(-str-) & RefLevel(-float-)
                    chPw = meas.VSA_get_chPwr()             # Get Ch Pwr(-float-)
                    time = datetime.datetime.now().strftime("%Y/%m/%d,%H:%M:%S")
                    totalTime = alT + evmT
                    data = f'{time},{freq:11},{pwr:3d},{refl:6.2f},{attn:2s},{chPw:6.2f},{EVM:6.2f},{lvling},{alT:6.3f},{evmT:6.3f},{totalTime:6.3f}'
                    self.file_write(data, endStr='')
                    self.calc_testtime()

if __name__ == '__main__':
    meas = std_insr_driver()
    EVM_Sweep().main()
