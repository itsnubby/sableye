"""
usb_camera.py - Python API for USB cameras.
sableye - sensor interface
Public:
    * USB_Camera(Sensor)
    * find_usb_cameras()
modified : 4/20/2020
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
    :out: usb_cameras [USB_Camera]
    """
    usb_cameras = []
    location = '/dev/video*'
    video_ports = glob.glob(location)
    unique_id = 0
    for address in video_ports:
        usb_camera = USB_Camera(unique_id, address)
#        try:
        usb_camera.set_up()
        usb_cameras.append(usb_camera)
        unique_id += 1
        say('Added USB camera from port '+str(address), 'success')
#        except:
#            say('Could not connect to USB camera at '+str(address), 'warning')
    return usb_cameras


class USB_Camera(Sensor):
    """
    Device class for USB-/OpenCV-enabled cameras.
    """
    def __init__(self, label, address, interface='opencv'):
        try:
            super().__init__(label, address, interface)
        except:
            super(USB_Camera, self).__init__(label, address, interface)
        
    def _fill_info(self):
        """
        Chat up the device to find where it lives as well
          as how to get into its front door.
        :in: old_info {dict} - any old metadata 'bout the device.
        :out: info {dict}
        """
        try:
            super()._fill_info()
        except:
            super(USB_Camera, self)._fill_info()
        self.info.update({'class': 'sensor'})
        
    def _get_device_id(self, label):
        """
        See that sensor.
        :in: label (int) Unique id
        :out: id (str)
        """
        # 'sensor' if not redefined.
        return '-'.join(['usb','camera',str(label)])

    def set_up(self,options={}):
        """
        Setup a USB camera.
        :out: success (Bool)
        :in: options {}
        """
        try:
            super().set_up(options=options)
        except:
            super(USB_Camera, self).set_up(options=options)

    def clean_up(self):
        """
        Close down shop.
        :out: success (Bool)
        """
        try:
            super().clean_up()
        except:
            super(USB_Camera, self).clean_up()
        return True
        
    def _connect(self):
        """
        Connect to a camera over OpenCV.
        """
        try:
            super()._connect()
        except:
            super(USB_Camera, self)._connect()
        try:
            self.channel = cv2.VideoCapture(self.address)
            self.status = 'standing_by'
        except:
            say(self.id+' cannot be opened', 'warning')
            self._disconnect()
        return True

    def _disconnect(self):
        """
        Close connection with a camera.
        """
        try:
            super()._disconnect()
        except:
            super(USB_Camera, self)._disconnect()
        try:
            self.channel.release()
        except:
            say(self.id+' not open.', 'warning')

    def _test_connection(self):
        """
        Check a port index through CV2.
        :in: port_index (int) cv2-friendly port to check
        :out: available (Bool) is device ready for communication?
        """
        if self.channel and self.channel.isOpened():
            return True
        return False

    def _stream_single(self):
        """
        <placeholder>
        """
        try:
            super()._stream()
        except:
            super(USB_Camera, self)._stream()

    def _stream_continuous(self):
        """
        <placeholder>
        """
        try:
            super()._stream()
        except:
            super(USB_Camera, self)._stream()

    def _stream_timelapse(self, frequency=1):
        """
        <placeholder>
        """
        try:
            super()._stream()
        except:
            super(USB_Camera, self)._stream()

def __test__usb_camera():
    usb_cameras = find_usb_cameras()
    for thing in usb_cameras:
       thing.set_up() 
    return 0

if __name__ == '__main__':
    __test__usb_camera()
