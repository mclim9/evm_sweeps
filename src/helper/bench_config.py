"""Bench Definition File"""
from iSocket import iSocket                 # Import socket module
import configparser

class bench():
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('src\\helper\\bench_config.ini')
        self.VSA_IP = config['Settings']['VSA_IP']
        self.VSG_IP = config['Settings']['VSG_IP']

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

    def set_inst_off(self):
        self.VSA.write(f':SYST:SHUT')
        self.VSG.write(f':SYST:SHUT')

if __name__ == '__main__':
    林 = bench().bench_verify()
    # 林.VSG_network_reset()
