"""Bench Definition File."""
try:
    from .iSocket import iSocket      # Package-level import for the class
except (ImportError, ValueError, ModuleNotFoundError):
    try:
        from iSocket import iSocket   # direct script execution fallback
    except ImportError:
        from src.helper.iSocket import iSocket # absolute fallback
import configparser


class BenchConfig:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read(f'{__file__[:-3]}.ini')
        self.VSA_IP = config['Settings']['VSA_IP']
        self.VSG_IP = config['Settings']['VSG_IP']

    def bench_verify(self):
        self.VSA = iSocket().open(self.VSA_IP, 5025)
        self.VSG = iSocket().open(self.VSG_IP, 5025)
        print()
        print(self.VSA.idn)
        print(self.VSG.idn)

    def VSA_start(self, ip=''):
        """Start VSA with given IP or default from config."""
        if ip:
            self.VSA_IP = ip
        self.VSA = iSocket().open(self.VSA_IP, 5025)
        return self.VSA

    def VSG_network_reset(self):
        self.VSG_start()
        self.VSG.query(f'SYST:COMM:NETW:REST;*OPC?')

    def VSG_start(self, ip=''):
        """Start VSG with given IP or default from config."""
        if ip:
            self.VSG_IP = ip
        self.VSG = iSocket().open(self.VSG_IP, 5025)
        return self.VSG

    def set_inst_off(self):
        self.VSA.write(':SYST:SHUT')
        self.VSG.write(':SYST:SHUT')


bench = BenchConfig


if __name__ == '__main__':
    林 = BenchConfig().bench_verify()
    # 林.VSG_network_reset()
