"""
i2c_device.py - Wrap your I2C devices up nicely in Python.
Radish'n'bots, LLC
     ) 0 o .
    modified : 2/10/2020
"""
import sys
if sys.version_info[0] < 3:
    print('Alas! I2C unsupported with this Pi below Python3!  ) 0 o .')
    sys.exit(1)
import Adafruit_ADS1x15
#import board
#import busio
#i2c = busio.I2C(board.SCL, board.SDA)
#import adafruit_ads1x15.ads1115 as ADS
#from adafruit_ads1x15.analog_in import AnalogIn

class ADC(object):
    """
    Wrapper for ADS1115 ADC.
    """
    def __init__(self):
        self.ads = ADS.ADS1115(i2c)
        self.chan = AnalogIn(self.ads, ADS.P0)

def test_i2c():
    """
    Ensure that all systems are a big GO.    ) 0 o .
    """
    # Edit overall test duration (s):
    test_duration = 60
    # Edit sampling frequency (Hz):
    f_sample = 0.5

    # Sample data from I2C sensors over the desired time frame.
    this_dude = ADS1115()
    print(this_dude.chan.value, this_dude.chan.voltage)

if __name__ == '__main__':
    print('Under construction...  ) 0 o .')
    test_i2c()
