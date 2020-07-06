"""
timelapse.py
     ) 0 o .
"""
import time
from sableye.sableye import Sableye


# glabols.
device_handler = None
sensors = []

def _set_up():
    global sensors, device_handler
    device_handler = Sableye()
    sensors = device_handler.find_sensors()
    device_handler.connect(sensors)
    time.sleep(3)
    for sensor in sensors:
        if not sensor._wait_for_('STANDING_BY'):
            sensors.remove(sensor)
            del sensor

def _run():
    global sensors, device_handler
    while(1<2):
        #device_handler.take_picture(sensors)
        device_handler.start_recording(sensors)
        time.sleep(30)
        device_handler.stop_recording(sensors)
        time.sleep(30)


def lapse_time():
    try:
        _set_up()
        _run()
    except KeyboardInterrupt:
        print('kraw')

if __name__ == '__main__':
    lapse_time()
