"""
v4l2_camera.py - for when all else fails.
     ) 0 o .
"""
import sys, time
try:
    from .device import Device, _MIN_PRIORITY, _MAX_PRIORITY, _DEFAULT_PRIORITY
except:
    from device import Device, _MIN_PRIORITY, _MAX_PRIORITY, _DEFAULT_PRIORITY


## GLOBALITIES.
# time stuff.
_CONNECT_TIMEOUT = 20               # 20s to connect.
_DISCONNECT_TIMEOUT = 10            # 10s to connect.
_TAKING_PIC_TIMEOUT = 10            # 10S to take a pic.
_DEFAULT_RECORD_TIME = 10           # 10s of streaming by default.
# video stuff.
_RESOLUTIONS = {
            '720p': {
                'width': 1280,
                'height': 720
                }
            }


## module definitions.
def find_v4l2_addresses():
    return []

def find_v4l2_cameras():
    """
    Hunt down and return any USB cameras.
    :out: v4l2_cameras [CV2_Camera]
    """
    v4l2_cameras = []
    v4l2_addresses = find_v4l2_addresses()
    for unique_id, address in enumerate(v4l2_addresses):
        v4l2_cameras.append(V4L2_Camera(str(unique_id), address))
    return v4l2_cameras


class V4L2_Camera(Device):
    """
    Device class for USB-/V4L2-enabled cameras.
    """

    def __init__(self, label, address):
        try:
            super().__init__(label, address)
        except:
            super(V4L2_Camera, self).__init__(label, address)
        self.streaming = multiprocessing.Value('i', 0)
        self.record_time = 0.0      # records indefinitely if record_time <= 0.0.
        self.channel = None
        self._resolution = _RESOLUTIONS['720p']
        #self._fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self._f_frames = 10.0     # <-- Change frames / s here.



def _test():
    v4l2_cameras = find_v4l2_cameras()
    try:
        for camera in v4l2_cameras:
            camera.connect()
            if not camera.is_connected():
                # clean up.
                v4l2_cameras.remove(camera)
                camera.disconnect()
                del camera()
        while(1<2):
            for camera in v4l2_cameras:
                camera.take_picture()
            time.sleep(1)
            for camera in v4l2_cameras:
                camera.start_recording()
            time.sleep(5)
            for camera in v4l2_cameras:
                camera.stop_recording()
            print('Good show.')
            time.sleep(1)
    except KeyboardInterrupt:
        print('Exiting.')
        sys.exit()

if __name__ == '__main__':
    _test()
