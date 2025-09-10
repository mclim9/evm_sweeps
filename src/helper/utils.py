# Utilities for EVM Sweep
import timeit
import numpy as np

def get_Array_stats(in_arry):
    avg = np.mean(in_arry)                          # Calc average
    min = np.min(in_arry)                           # Calc minimum
    max = np.max(in_arry)                           # Calc maximum
    std_dev = np.std(in_arry)                       # Calc standard deviation
    out_str = f'Min:{min:.3f} Max:{max:.3f} Avg:{avg:.3f} StdDev:{std_dev:.3f} Delta:{max - min:.3f}'
    print(out_str)
    return out_str

def method_timer(method):
    def wrapper(*args, **kwargs):
        start_time = timeit.default_timer()         # Start the timer
        result = method(*args, **kwargs)            # Call the actual method
        stop_time = timeit.default_timer()          # Stop the timer
        delta_time = stop_time - start_time         # Calculate the elapsed time
        # print(f"    {method.__name__:15s}: {delta_time:.3f} secs")
        return result, delta_time
    return wrapper

def std_config(林):
    林.VSG_Config()
    林.VSA_Config()
    林.VSx_freq(林.freq)
    林.VSA_sweep()
    林.VSG.clear_error()
    林.VSA.clear_error()

def std_meas(林):
    林.VSA_get_info()
    林.VSA_sweep()
    林.VSA_level()
    EVMM = 林.VSA_get_EVM()[0]
    ACLR = 林.VSA_get_ACLR()[0]
    chPw = 林.VSA_get_chPwr()
    print(f'EVM:{EVMM:.2f} CH_Pwr:{chPw:.2f} ACLR:{ACLR}')

@method_timer
def test(inString):
    sum(range(1000000))
    print(f'{inString}')


if __name__ == '__main__':
    test("mud")
