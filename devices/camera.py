"""
camera.py - Webcam API for the FUTURE.
Radish'n'bots, LLC
     ) 0 o .
    modified : 2/12/2020
"""
import time
try:
    import picamera
except:
    print(str(ImportError))
    import cv2 as picamera
try:
    from .device import Device
except:
    from device import Device
import os
import io
import copy
import sys
import cv2
import datetime
import glob
import subprocess as sp

## Global declarations or something.
_EPOCH = datetime.datetime(1970,1,1)
_RESOLUTIONS = {
    '1080p': {
    'width': 1920,
    'height': 1080
    },
    '720p': {
    'width': 1280,
    'height': 720
    }
    }
_FORMATS = {
    'image': ['png', 'jpg'],
    'video': ['mp4']
    }
_DEFAULT = {
    'video_format': 'mp4',
    'image_format': 'png',
    'resolution': '1080p'
    }

_CAMERA_STATES = [
        'init',
        'setting_up',
        'idling',
        'streaming',
        'sleeping']

## Local functions.
def _get_time_now(time_format='utc'):
    """
    Thanks Jon.    (;
    :in: time_format (str) ['utc','epoch']
    :out: timestamp (str)
    """
    if time_format == 'utc' or time_format == 'label':
        return datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    elif time_format == 'epoch' or time_format == 'timestamp':
        td = datetime.datetime.utcnow() - _EPOCH
        return str(td.total_seconds()).replace('.','_')
    else:
        # NOTE: Failure to specify an appropriate time_format will cost
        #         you one layer of recursion! YOU HAVE BEEN WARNED.    ) 0 o .
        return _get_time_now(time_format='epoch')


# TODO: Import from Device class.
class Camera(Device):
    def __init__(
        self, device_address, device_class='camera',
        serial_number='', device_type='usb-cvcamera'):
        self.timelapse = False      # Timelapse indicator.
        try:
            super().__init__(device_address, device_class, serial_number, device_type)
        except:
            super(Camera, self).__init__(device_address, device_class, serial_number, device_type)

    def _query_info(self, old_info={}):
        """
        Chat up the device to find where it lives as well
                as how to get into its front door.
        :in: old_info {dict} - any old metadata 'bout the device.
        :out: info {dict}
        """
        info = {
            'serial_number': '',
            'device_class': 'camera',
            'device_type': 'generic',
            'image_format': 'png',
            'video_format': 'h264',
            'device_address': self.device_address,
            'resolution': '720p',
            'framerate': 15
            }
        info.update(old_info)
        print(info)
        return info

    def _get_device_id(self):
        """
        Hunt down the device ID.
        :out: serial_number (str)
        """
        unique_ids = [
            self.info['device_type'],
            self.info['serial_number'],
            self.info['device_address'].replace('/','_')]
        return '-'.join(unique_ids)


    def set_up(self):
        """
        1. Verify that address of device specifies a valid OpenCV index.
        """
        # TODO: (nubby) enter the V4L-zone...
        available = False
        if not available:
            print(''.join([
                    'ERROR : Unable to communicate with camera source ',
                    self.device_address,'!']))
            raise ConnectionError

    def _record_picamera(self):
        """
        """
        camera = picamera.PiCamera(framerate=framerate)
        stream = picamera.PiCameraCircularIO(camera, seconds=seconds)
        if preview is True:
            camera.start_preview()
            camera.start_recording(stream, format=format)
            time.sleep(seconds)
            camera.stop_recording()
            camera.stop_preview()
        else:
            camera.start_recording(stream, format=format)
            time.sleep(seconds)
            camera.stop_recording()
        camera.close()
        for frame in stream.frames:
            if frame.header:
                stream.seek(frame.position)
                break
        with io.open(self.saveDir + 'video.h256', 'wb') as output:
            data = stream.read1()
            while data:
                output.write(data)
                data = stream.read1()
        return
    
    def _record_usbcamera(self):
        """
        """
        try:
            resolution = self.info['resolution']
            frame_w = _RESOLUTIONS[resolution]['width']
            frame_h = _RESOLUTIONS[resolution]['height']
        except:
            print(''.join([
                'WARNING : Resolution ', self.info['resolution'],
                ' unsupported; default to ', _DEFAULT['resolution'],'.']))
            resolution = _DEFAULT['resolution']
            frame_w = _RESOLUTIONS[resolution]['width']
            frame_h = _RESOLUTIONS[resolution]['height']

        ## Get image format.
        image_format = self.info['image_format']
        if not image_format in _FORMATS['image']:
            print(''.join([
                'WARNING : Picture format ', self.info['image_format'],
                ' unsupported; default to ', _DEFAULT['image_format'],'.']))
            image_format = _DEFAULT['image_format']

        ## Generate image label.
        timestamp = _get_time_now('timestamp')
        image_label = '.'.join([
            '-'.join([
                self.base_data_path+timestamp,
                str(self.device_address),
                label]),
            image_format])

        ## Take a pic.
        cam = cv2.VideoCapture(int(self.device_address))
        ret, frame = cam.read()
        cv2.imwrite(image_label, frame)
        cv2.destroyAllWindows()
        cam.release()

        ## Verify that file exists.
        if not os.path.isfile(image_label):
            print('WARNING : Picture not taken!')

    def record(self, mode='default', label='test'):
        """
        Take a picture or begin streaming video depending on mode.
        :in: mode (str) - [default [single], single (picture), timed, continuous]
        :in: label (str)
        """
        try:
            super().record()
        except:
            super(Camera, self).record()
    
    def stop(self):
        """
        """
        try:
            super().stop()
        except:
            super(Camera, self).stop()
        

    def clean_up(self):
        """
        Take out the trash.
        """
        return

    def _timelapse(self, samples_per_day):
        """
        Timelapse thread.
        :in: samples_per_day (int)
        """
        self.timelapse = True
        if self.info['device_type'] == 'pi-camera':
            self._pimelapse(samples_per_day)
        elif self.info['device_type'] == 'usb-camera':
            self._usb_timelapse(samples_per_day)
        else:
            say('Recording not supported on '+str(self.info['device_type']), 'warning')

    
    def start_timelapse(self, samples_per_day=3):
        """
        :in: samples_per_day (int)
        """
        _start_thread(_timelapse, samples_per_day)


    # Aliases.
    take_picture = record

class USB_Camera(Camera):
    """
    Camera class for OpenCV communications.
    """
    def __init__(
        self, device_address,
        serial_number='', device_type='usb-camera'):
        self.timelapse = False      # Timelapse indicator.
        try:
            super().__init__(device_address, device_class, serial_number, device_type)
        except:
            super(USB_Camera, self).__init__(device_address, device_class, serial_number, device_type)

    def _query_info(self, old_info={}):
        """
        Chat up the device to find where it lives as well
                as how to get into its front door.
        :in: old_info {dict} - any old metadata 'bout the device.
        :out: info {dict}
        """
        info = {
            'serial_number': '',
            'device_class': 'camera',
            'device_type': 'usb-camera',
            'image_format': 'png',
            'video_format': 'mp4',
            'device_address': self.device_address,
            'resolution': '720p',
            'framerate': 15
            }
        info.update(old_info)
        print(info)
        return info

    def _verify_cv2_port(port_index):
        """
        Check a port index through CV2.
        :in: port_index (int) cv2-friendly port to check
        :out: available (bool) is device ready for communication?
        """
        available = False
        cam = cv2.VideoCapture(port_index)
        if cam and cam.isOpened():
            available = True
            cam.release()
        return available

    def set_up(self):
        """
        1. Verify that address of device specifies a valid OpenCV index.
        """
        # TODO: (nubby) enter the V4L-zone...
        available = False
        available = self._verify_cv2_port(int(self.device_address))
        if not available:
            print(''.join([
                    'ERROR : Unable to communicate with camera source ',
                    self.device_address,'!']))
            raise ConnectionError

    def record(self, mode='default', label='test'):
        """
        Take a picture or begin streaming video depending on mode.
        :in: mode (str) - [default [single], single (picture), timed, continuous]
        :in: label (str)
        """
        try:
            super().record()
        except:
            super(USB_Camera, self).record()
        try:
            resolution = self.info['resolution']
            frame_w = _RESOLUTIONS[resolution]['width']
            frame_h = _RESOLUTIONS[resolution]['height']
        except:
            print(''.join([
                'WARNING : Resolution ', self.info['resolution'],
                ' unsupported; default to ', _DEFAULT['resolution'],'.']))
            resolution = _DEFAULT['resolution']
            frame_w = _RESOLUTIONS[resolution]['width']
            frame_h = _RESOLUTIONS[resolution]['height']

        ## Get image format.
        image_format = self.info['image_format']
        if not image_format in _FORMATS['image']:
            print(''.join([
                'WARNING : Picture format ', self.info['image_format'],
                ' unsupported; default to ', _DEFAULT['image_format'],'.']))
            image_format = _DEFAULT['image_format']

        ## Generate image label.
        timestamp = _get_time_now('timestamp')
        image_label = '.'.join([
            '-'.join([
                self.base_data_path+timestamp,
                str(self.device_address),
                label]),
            image_format])

        ## Take a pic.
        cam = cv2.VideoCapture(int(self.device_address))
        ret, frame = cam.read()
        cv2.imwrite(image_label, frame)
        cv2.destroyAllWindows()
        cam.release()

        ## Verify that file exists.
        if not os.path.isfile(image_label):
            print('WARNING : Picture not taken!')
    
    def stop(self):
        """
        """
        try:
            super().stop()
        except:
            super(USB_Camera, self).stop()
        

    def clean_up(self):
        """
        Take out the trash.
        """
        return

    def _timelapse(self, samples_per_day):
        """
        Timelapse thread.
        :in: samples_per_day (int)
        """
        self.timelapse = True
        if self.info['device_type'] == 'pi-camera':
            self._pimelapse(samples_per_day)
        elif self.info['device_type'] == 'usb-camera':
            self._usb_timelapse(samples_per_day)
        else:
            say('Recording not supported on '+str(self.info['device_type']), 'warning')


class Pi_Camera(Camera)
    def __init__(
        self, device_address,
        serial_number='', device_type='pi-camera'):
        self.timelapse = False      # Timelapse indicator.
        try:
            super().__init__(device_address, device_class, serial_number, device_type)
        except:
            super(Pi_Camera, self).__init__(device_address, device_class, serial_number, device_type)

class Webcam(object):
    def __init__(self,camera_type='PiCamera'):
        self.saveDir = '/home/pi/Desktop/camera/'
        self.image_format = '.jpg'
        self.camera_type = camera_type

    def record_video(self, seconds=20, framerate=60, preview=True, format='h264'):
        camera = picamera.PiCamera(framerate=framerate)
        stream = picamera.PiCameraCircularIO(camera, seconds=seconds)
        if preview is True:
            camera.start_preview()
            camera.start_recording(stream, format=format)
            time.sleep(seconds)
            camera.stop_recording()
            camera.stop_preview()
        else:
            camera.start_recording(stream, format=format)
            time.sleep(seconds)
            camera.stop_recording()
        camera.close()
        for frame in stream.frames:
            if frame.header:
                stream.seek(frame.position)
                break
        with io.open(self.saveDir + 'video.h256', 'wb') as output:
            data = stream.read1()
            while data:
                output.write(data)
                data = stream.read1()

    def timelapse_photos(self, image_name='', append_time=True, interval=10, length_of_time=31536000):
        camera = picamera.PiCamera()
        iterations = int(length_of_time / interval)
        try:
            if append_time is True:
                for i in range(iterations):
                    camera.capture(self.saveDir + str(datetime.datetime.now()) + image_name + str(i) + self.image_format)
                    time.sleep(interval)
            else:
                for i in range(iterations):
                    camera.capture(self.saveDir + image_name + str(i) + self.image_format)
                    time.sleep(interval)
        finally:
            camera.close()

    def take_photo(self, image_name='', append_time=True):
        camera = picamera.PiCamera()
        try:
            if append_time is True:
                camera.capture(self.saveDir + str(datetime.datetime.now()) + image_name + str(i) + self.image_format)
                time.sleep(interval)
            else:
                camera.capture(self.saveDir + image_name + str(i) + self.image_format)
                time.sleep(interval)
        finally:
                        camera.close()


def check_camera_can_open(address):
    """
    Verify that a camera can be opened at a given address.
    :in: address (str)
    :out: funk (Bool)
    """
    funk = False
    cam = cv2.VideoCapture(address)
    if cam and cam.isOpened():
        funk = True
    cam.release()
    return funk

def find_cameras():
    """
    Identify any connected USB cameras and return them as a list.
    :out: available [{camera_info}] - {device_type: camera, device_address: <CV2_REF>, serial_number: <SERIAL_NUM>}
    """
    camera_info_template = {
            'device_type': 'camera',
            'device_address': -1,
            'serial_number': ''}
    available = []  # Available camera indices.
    cameras = []    # Formatted camera dictionaries.
    # Check which cameras the system finds.
    homes = ['/dev/video*']
    camera_addresses = []
    for ls in homes:
        camera_addresses += glob.glob(ls)
    # Linux shows multiple camera devices for a single camera.
    for addr in camera_addresses:
        dev_index = int(addr.split('video')[-1])
        if dev_index < 10:
            device_type = 'usb-camera'
        else:     # Picamera
            device_type = 'pi-camera'
            if not check_picamera_can_open():       # Assume that only one Picamera can be connected to a Pi at a time.
                

    total_camera_num = int(len(camera_addrs) / 2)
    available = range(0,total_camera_num+1,1)
    # Try to open each camera.
    for index in available:
        if not check_camera_can_open(index):
            continue
        thing = copy.deepcopy(camera_info_template)
        thing['device_address'] = index
#       TODO: thing['serial_number'] = serial_number
        thing['serial_number'] = str(index)
        cameras.append(thing)

    return cameras

def test_camera():
    # Set up.
    base_dc_dir = './test_data/'
    if not os.path.isdir(base_dc_dir):
        os.mkdir(base_dc_dir)
    # Find each available camera.
    cameras_info = find_cameras()

    # Test the camera.
    for device in cameras_info:
        cam = Camera(device['device_address'])
        try:
            cam.set_up()
        except:
            print(''.join([
                'ERROR : Camera at ',
                str(device_address),
                ' not connected!']))

        cam.set_data_path(base_dc_dir)
        cam.record('yellow_oyster', 'continuous')
        cam.clean_up()

if __name__ == '__main__':
    test_camera()

#cam = Webcam()
#cam.timelapse_photos(interval=5, image_name='test', length_of_time=60)
#cam.record_video(seconds=10, preview=True)
