"""
sableye.py - control this from mawile.
modified : 5/30/2020
     ) 0 o .
"""
import re
try:
    from .devices.i2c_adc import ADS1115, find_i2c_devices
except:
    from devices.i2c_adc import ADS1115, find_i2c_devices
try:
    from .devices.cv2_camera import CV2_Camera, find_cv2_cameras
except:
    from devices.cv2_camera import CV2_Camera, find_cv2_cameras


## globals.
_AVAILABLE_I2C_ADDRESSES = []
_AVAILABLE_USB_ADDRESSES = []
_AVAILABLE_CV2_ADDRESSES = []


## helpers.
# temp.
def find_usb_sensors():
    usb_devices = []
    return usb_devices

def printf(blurb, flag='status'):
    preamble = str(flag).upper() + ' : '
    blurb = preamble + blurb
    print(blurb)

class Sableye():
    def __init__(self):
        printf('Sableye created')

    ##finders.
    def find_sensors(self):
        # Find available eyes/ears/tongues/etc.
        sensors = []
        sensors += find_i2c_devices()
        sensors += find_usb_sensors()
        sensors += find_cv2_cameras()
        return sensors

    # Find available heads.
    def find_controllers(self):
        pass

    # Find available limbs.
    def find_mech(self):
        pass


    def find_devices(self):
        sensors = self.find_sensors()
        controllers = self.find_controllers()
        mech = self.find_mech()
        return sensors, controllers, mech

    ## actions.
    def connect(self, devices):
        for device in devices:
            try:
                device.connect()
            except:
                printf('Cannot connect to device, '+str(device), 'warning')

    def disconnect(self, devices):
        for device in devices:
            try:
                device.disconnect()
            except:
                printf('Cannot disconnect from device, '+str(device), 'warning')

    def start_recording(self, devices, duration=0.0):
        for device in devices:
            try:
                device.start_recording(duration=duration)
            except:
                printf('Cannot start recording with device, '+str(device), 'warning')

    def stop_recording(self, devices):
        for device in devices:
            try:
                device.stop_recording(duration=duration)
            except:
                printf('ERROR! Cannot stop recording with device, '+str(device), 'warning')

    def turn_on(self, devices):
        for device in devices:
            try:
                device.turn_on(duration=duration)
            except:
                printf('ERROR! Cannot turn on device, '+str(device), 'warning')

    def turn_off(self, devices):
        for device in devices:
            try:
                device.turn_off(duration=duration)
            except:
                printf('ERROR! Cannot turn off device, '+str(device), 'warning')

    def take_picture(self, sensors):
        for sensor in sensors:
            try:
                sensor.take_picture()
            except:
                printf('WARNING: Cannot take picture with sensor, '+str(sensor), 'warning')


# tests.
def shadow_ball():
    device_handler = Sableye()
    sensors = device_handler.find_sensors()
    controllers = device_handler.find_controllers()
    mech = device_handler.find_mech()

def lapse_time():
    device_handler = Sableye()
    sensors = device_handler.find_sensors()
    device_handler.connect(sensors)


if __name__ == '__main__':
    lapse_time()
    #shadow_ball()
