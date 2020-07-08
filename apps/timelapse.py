"""
timelapse.py
     ) 0 o .
"""
import sys, time, argparse
from sableye.sableye import Sableye


# glabols.
device_handler = None
sensors = []

def _set_up(base_path='./'):
    global sensors, device_handler
    device_handler = Sableye(base_path=base_path)
    device_handler.set_up(base_path=base_path)
    print(str(sensors))
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


def lapse_time(path='./'):
    try:
        _set_up(base_path=path)
        _run()
    except KeyboardInterrupt:
        print('kraw')

def parse():
    parser = argparse.ArgumentParser(description='collect data blurbs indefinitely.')
    parser.add_argument('--path', type=str, default='~/pkgs/sableye/apps/test_data/', help='data path')
    return parser.parse_args()

if __name__ == '__main__':
    parsed = parse()
    lapse_time(path=parsed.path)
