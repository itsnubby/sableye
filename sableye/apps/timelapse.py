"""
timelapse.py
     ) 0 o .
"""
from sableye.sableye import Sableye

def lapse_time():
    device_handler = Sableye()
    devices = device_handler.find_devices()

if __name__ == '__main__':
    lapse_time()
