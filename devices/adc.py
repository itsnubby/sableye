"""
adc.py - Communicate with the ADS1115 ADC like a champ, Champ.
Radish'n'bots, LLC
     ) 0 o .
    modified : 2/12/2020
"""
try:
    from device import 
import Adafruit_ADS1x15
import time

# To install this package on the raspberry pi, use:
#
# sudo apt-get update
# sudo apt-get install build-essential python-dev python-smbus python-pip
# sudo pip install adafruit-ads1x15
#
# Additional information available from Adafruit:
# https://learn.adafruit.com/raspberry-pi-analog-to-digital-converters/ads1015-slash-ads1115

class ADC(Device):
    def __init__(self, adc_address=0x48, i2c_bus=1):
        self.i2c_bus = i2c_bus             # default: 1 (0 on older pi's)
        self.adc_address = adc_address     # default: 0x48
        self.adc_i = Adafruit_ADS1x15.ADS1115(address=adc_address, busnum=i2c_bus)
        print("Connected sensor: ADS1115 @ " + str(self.adc_address))

    def readADC(self, adc_pin_address, adc_gain):
        return self.adc_i.read_adc(adc_pin_address, adc_gain)

def milk():
    """
    Test ADCs!
    """
    thing = ADC()
    while(1<2):
        print(thing.readADC(3,1))
        time.sleep(0.1)


if __name__ == '__main__':
    milk()
