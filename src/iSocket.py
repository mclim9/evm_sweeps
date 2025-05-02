"""Rohde & Schwarz instrument socket for demonstration use."""
import logging
import socket
import timeit
import time

class iSocket():
    """ instrument socket class """
    def __init__(self):
        self.s = socket.socket()                # Create a socket

    def close(self):
        self.s.close()

    def clear_error(self):
        num_error = 0
        for i in range(10):
            rdStr = self.query('SYST:ERR?')
            print(f'Error: {rdStr}')
            errorCode = rdStr.split(',')[0]
            if errorCode == '0':
                break
            else:
                num_error += 1
        return num_error

    def delay(self, seconds):
        time.sleep(seconds)

    def logging_test(self, log_file):
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

        logger = logging.getLogger('asdf')
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

        return logger

    def opc(self, SCPI):
        self.write("*ESE 1")                    # Event Status Enable
        self.write("*SRE 32")                   # SRE Def: Bit5:Std Event
        self.write(f"{SCPI};*OPC")              # *OPC will trigger ESR
        read = 0
        while (read & 1) != 1:                  # Loop until done
            read = self.queryInt("*ESR?")       # Poll ESB
            time.sleep(0.5)
            if time.delta > 300:              # Timeout
                break

    def open(self, host, port):
        """connect instrument socket"""
        try:
            logging.basicConfig(level=logging.DEBUG,
                                filename=__file__.split('.')[0] + '.log', filemode='a',         # noqa:
                                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # noqa:
            self.s.connect((host, port))
            self.s.settimeout(5)                    # Timeout(seconds)
            self.idn = self.query('*IDN?')
            # print(f'IDN  : {self.idn}')
        except socket.error:
            print(f"SckErr: {socket.error}")
        return self

    def query(self, SCPI):                          # noqa: E302
        """Socket Query"""
        self.write(SCPI)
        # print(f'iSckt> {SCPI}  ', end='')
        # print(f'iSckt> {SCPI}  ')
        time.sleep(.001)
        try:
            sOut = self.s.recv(10000000).strip()    # Read socket
            sOut = sOut.decode()
        except socket.error:
            sOut = '<not Read>'
        logging.info(f'Read < {sOut}')
        # print(f'Read < {sOut}')
        return sOut

    def queryFloat(self, SCPI):
        rdStr = self.query(SCPI)
        return float(rdStr)

    def queryInt(self, SCPI):
        rdStr = self.query(SCPI)
        return int(rdStr)

    def read(self):
        n = 10000000
        try:
            sOut = bytearray()
            while len(sOut) < n:
                packet = self.s.recv(n - len(sOut))
                if not packet:
                    return None
                sOut.extend(packet)
                if sOut[-1] == 10:
                    # sOut = sOut.decode()
                    break
        except socket.error:
            sOut = '<not Read>'
        return sOut

    def tick(self):
        self.ticks = timeit.default_timer()

    def tock(self, comment=''):
        self.tocks = timeit.default_timer() - self.ticks
        if comment != '':
            print(f'Time : {self.tocks:7.3f} secs {comment}')
        return self.tocks

    def timeout(self, seconds):
        self.s.settimeout(seconds)

    def write(self, SCPI):                          # noqa: E302
        """Socket Write"""
        logging.info(f'Write> {SCPI.strip()}')
        self.s.sendall(f'{SCPI}\n'.encode())        # Write 'SCPI'

    def writeBin(self, SCPI):                       # noqa: E302
        """Socket Write"""
        logging.info(f'Write> {SCPI.strip()}')
        self.s.sendall(SCPI + bytes([10]))          # Write 'SCPI'

if __name__ == "__main__":
    instr = iSocket().open('192.168.58.109', 5025)
    instr.opc('INIT:IMM')
    print(instr.query('*IDN?'))
