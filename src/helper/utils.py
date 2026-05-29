import numpy as np
import timeit
from helper.bench_config import BenchConfig         # When root (src/)

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

def vsa_meas_EVM(林):
    林.vsa_configure()
    林.vsa_set_frequency(6e9)
    林.vsa_sweep()
    林.vsa_set_level('MAN')
    林.vsa_get_evm()


if __name__ == '__main__':
    from driver.K18_vsa_fsw import VSA_driver

    bench = BenchConfig()
    # Ensure both VSA and VSG are passed if the driver requires them
    林 = VSA_driver(bench.VSA_start())
    vsa_meas_EVM(林)
