import spidev
import time

class Mcp:

    spi = spidev.SpiDev()  # create spi object
    kanalen = [0x80, 0x90, 0xa0, 0xb0, 0xc0, 0xd0, 0xe0, 0xf0]

    def __init__(self, bus=0, device=0):
        self.bus = bus
        self.device = device
        self.spi.open(self.bus, self.device)  # open spi port 0, device (CS) 0
        self.spi.max_speed_hz = 10 ** 5  # 100 kHz

    def read_channel(self, ch):
        return self.__voeg_bytes_samen(self.spi.xfer2([0x01, self.kanalen[ch], 0x42]))

    def __voeg_bytes_samen(self, bytes):
        return bytes[1] << 8 | bytes[2]