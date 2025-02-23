import spidev # type: ignore
import time

class PAW3395:
    def __init__(self, bus=0, device=0, max_speed_hz=10000000):
        self.spi = spidev.SpiDev()
        self.bus = bus
        self.device = device
        self.spi.open(bus, device)
        self.spi.max_speed_hz = max_speed_hz
        self.spi.mode = 3 #CPOL=1, CPHA=1 in datasheet
    
    def write_register(self, reg, value):
        reg |= 0x80 #Set MSB to 1 for write operation
        self.spi.xfer2([reg, value])
        time.sleep(0.000005) #tSWW delay (5 µs)
    
    def read_register(self, reg):
        reg &= 0x7F #Set MSB to 0 for read operation
        response = self.spi.xfer2([reg, 0x00])
        time.sleep(0.000002) #tSRAD delay (2 µs)
        return response[1]

    def motion_burst_read(self):
        self.spi.xfer2([0x16]) #Motion_Burst register
        time.sleep(0.000002) #tSRAD delay
        data = self.spi.xfer2([0x00] * 12)  # Read 12 bytes
        return {
            "motion": data[0],
            "delta_x": (data[3] << 8) | data[2],
            "delta_y": (data[5] << 8) | data[4],
            "squal": data[6],
            "rawdata_sum": data[7],
            "max_rawdata": data[8],
            "min_rawdata": data[9],
            "shutter_upper": data[10],
            "shutter_lower": data[11]
        }

    def power_up_sequence(self): #Power up initialization sequence
        self.write_register(0x3A, 0x5A) #Power_up_reset
        time.sleep(0.005) #5ms delay
        self.write_register(0x7F, 0x07)
        self.write_register(0x40, 0x41)
        self.write_register(0x55, 0x04)
        self.write_register(0x58, 0xFF)
        while not (self.read_register(0x59) & 0x03): #Wait for PG_FIRST and PG_VALID
            time.sleep(0.001)
        self.write_register(0x40, 0x00)
        self.write_register(0x50, 0x00)
        self.write_register(0x55, 0x00)

    def close(self):
        self.spi.close()