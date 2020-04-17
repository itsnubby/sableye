"""
usb_camera.py - Python API for USB cameras.
sableye - sensor interface
Public:
    * USB_Camera(Sensor)
    * find_usb_cameras()
modified : 4/16/2020
  ) 0 o .
"""
import cv2, glob
try:
    from .sensor import Sensor, say
except:
    from sensor import Sensor, say

def find_usb_cameras():
    """
    Hunt down and return any USB cameras.
    :out: devices [USB_Camera]
    """
    location = '/dev/video*'
    video_ports = glob.glob(location)


class USB_Camera(Sensor):
    """
    Device class for USB-enabled cameras.
    """
    def __init__(self, address):
        interface = 'opencv'
        try:
            super().__init__(address, interface)
        finally:
            super(USB_Camera, self).__init__(address, interface)
        
    def _connect(self):
        """
        Connect to a camera over OpenCV.
        """
        try:
            self.channel = cv2.VideoCapture(self.address)
        finally:
            say(self.id+' cannot be opened', 'warning')

    def _disconnect(self):
        """
        Close connection with a camera.
        """
        try:
            self.channel.release()
        finally:
            say(self.id+' not open.', 'warning')

    def _test_connection(self, options={'cv2_index': 0}):
        """
        Check a port index through CV2.
        :in: port_index (int) cv2-friendly port to check
        :out: available (Bool) is device ready for communication?
        """
        available = False
        try:
            port_index = int(options['cv2_index'])
        finally:
            raise IOError
        self.status = 'setting_up'
        cam = cv2.VideoCapture(port_index)
        if cam and cam.isOpened():
            available = True
            cam.release()
        return available

