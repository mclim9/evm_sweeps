"""Bench Definition File"""
from iSocket import iSocket                 # Import socket module

class bench():
    def __init__(self):
        self.VSA_IP = 'FSW50-101877'        # 172.24.225.101
        self.VSA_IP = '172.24.225.101'      # FSW50-101877

        self.VSG_IP = 'SMW200A-111623'      # Old
        self.VSG_IP = '172.24.225.210'      # SMW200A-111623
        self.VSG_IP = '172.24.225.128'      # SMM100A-110005
        self.VSG_IP = 'SMM100A-110005'      # SMM100A-110005
        self.VSG_IP = 'SMW200A-120095'      # 2xRF

    def bench_verify(self):
        self.VSA = iSocket().open(self.VSA_IP, 5025)
        self.VSG = iSocket().open(self.VSG_IP, 5025)
        print()
        print(self.VSA.idn)
        print(self.VSG.idn)

    def VSA_start(self):
        self.VSA = iSocket().open(self.VSA_IP, 5025)
        return self.VSA

    def VSG_network_reset(self):
        self.VSG_start()
        self.VSG.query(f'SYST:COMM:NETW:REST;*OPC?')

    def VSG_start(self):
        self.VSG = iSocket().open(self.VSG_IP, 5025)
        return self.VSG

    def set_freq(self, freq):
        self.VSA.write(f':SENS:FREQ:CENT {freq}')
        self.VSG.write(f':SOUR1:FREQ:CW {freq}')

if __name__ == '__main__':
    林 = bench()
    林.bench_verify()
    # 林.VSG_network_reset()
    林.set_freq(2e9)
