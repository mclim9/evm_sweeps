# Utilities for EVM Sweep
import timeit

def method_timer(method):
    def wrapper(*args, **kwargs):
        start_time = timeit.default_timer()         # Start the timer
        result = method(*args, **kwargs)            # Call the actual method
        stop_time = timeit.default_timer()          # Stop the timer
        delta_time = stop_time - start_time         # Calculate the elapsed time
        print(f"{method.__name__:15s}: {delta_time:.3f} secs")
        return result
    return wrapper

def std_config(林):
    林.VSG_Config()
    林.VSA_Config()
    林.set_VSx_freq(林.freq)
    林.get_VSA_sweep()
    林.VSG.clear_error()
    林.VSA.clear_error()

def std_meas(林):
    林.get_info()
    林.set_VSA_init()
    林.set_VSG_init()
    林.get_VSA_sweep()
    EVMM = 林.get_EVM()
    ACLR = 林.get_ACLR()
    chPw = 林.get_VSA_chPwr()
    print(f'EVM:{EVMM:.2f} CH_Pwr:{chPw:.2f} ACLR:{ACLR}')

@method_timer
def test(inString):
    sum(range(1000000))
    print(f'{inString}')


if __name__ == '__main__':
    test("mud")
