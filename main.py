import time
from paw3395 import PAW3395


sensor = PAW3395()
sensor.power_up_sequence()
print("Product ID:", hex(sensor.read_register(0x00)))
print("Motion data:", sensor.motion_burst_read())