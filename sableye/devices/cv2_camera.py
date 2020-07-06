"""
cv2_camera.py - Python API for USB cameras.
sableye - sensor interface
Public:
    * CV2_Camera(Sensor)
    * find_cv2_cameras()
modified : 7/6/2020
     ) 0 o .
"""
import sys, copy, cv2, glob, time, os, datetime, multiprocessing
import subprocess as sp
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


## module definitions. [TODO : make part of interface class]
def _parse_v4l2_info(v4l2_str):
    device_fields = v4l2_str.split(' ')
    device_class = device_fields[0].split(':')[0]
    try:
        device_mac = device_fields[2][1:-2]
        device_name = device_fields[1]
    except:
        device_mac = ''
        device_name = device_fields[1]
    device_info = {
            'device_name': device_name,
            'device_class': device_class,
            'device_mac_address': device_mac,
            'device_ports': []
            }
    return device_info
    
def _add_camera_port(port, device_info):
    port_nums = []
    device_info['device_ports'].append(port)
    for port in device_info['device_ports']:
        try:
            port_nums.append(int(port.split('/dev/video')[1]))
        except:
            print('Warning! Video port format not recognized')
    device_info['device_cv2_index'] = min(port_nums)

def find_v4l2_info():
    cv2_devices_info = []
    _shellosh = [
            'v4l2-ctl',
            '--list-devices'
            ]
    try:
        _cv2_list_proc = sp.Popen(_shellosh, stdout=sp.PIPE)
    except:
        print('Could not communicate with that darn shell!')
        return cv2_devices_info
    # parse out cv2 info.
    _address_indic = '/dev/video'
    device_info = {}
    _cv2_info = str(_cv2_list_proc.communicate()[0].decode(encoding='UTF-8')).strip()
    for _cv2_line_str in _cv2_info.split('\n'):
#        _cv2_line_str = str(_cv2_list_proc.stdout.readline().decode(encoding='UTF-8')).strip()
        # exit loop if out of lines.
        if _cv2_line_str == '':
            continue
        # check for camera labels.
        elif not _address_indic in _cv2_line_str:
            # ensure that camera is a USB camera or continue (TODO : add picams).
            try:
                device_info = _parse_v4l2_info(_cv2_line_str)
            except:
                continue
            cv2_devices_info.append(device_info)
        else:
            _add_camera_port(_cv2_line_str, device_info)
    return cv2_devices_info

def find_cv2_cameras():
    """
    Hunt down and return any USB cameras.
    :out: cv2_cameras [CV2_Camera]
    """
    cv2_cameras = []
    cv2_devices_info = find_v4l2_info()
    for device_info in cv2_devices_info:
        # skip picamera entries for now.
        if device_info['device_cv2_index'] > 9:
            continue
        cv2_label = '-'.join([
            device_info['device_name'],
            str(device_info['device_cv2_index'])])
        cv2_cameras.append(
                CV2_Camera(
                    cv2_label,
                    device_info['device_cv2_index'],
                    info=device_info))
    return cv2_cameras


class CV2_Camera(Device):
    """
    Device class for USB-/OpenCV-enabled cameras.
    """

    def __init__(self, label, address, info={}):
        try:
            super().__init__(label, address)
        except:
            super(CV2_Camera, self).__init__(label, address)
        self.streaming = multiprocessing.Value('i', 0)
        self.record_time = 0.0      # records indefinitely if record_time <= 0.0.
        self.channel = None
        self._resolution = _RESOLUTIONS['720p']
        self._fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self._f_frames = 10.0     # <-- Change frames / s here.

    def __str__(self):
        try:
            return str(self.id)
        except:
            return 'cv2_camera'

    # redefined, read ya mind.
    def _set_up_events(self):
        self._add_event('NO_EVENT', _MIN_PRIORITY)
        self._add_event('INIT_EVENT', _MAX_PRIORITY)
        self._add_event('EXIT_EVENT', _MIN_PRIORITY)
        self._add_event('COMPLETE_EVENT', _DEFAULT_PRIORITY)
        self._add_event('CONNECTED_EVENT', _MAX_PRIORITY)
        self._add_event('RECORDING_COMPLETE_EVENT', _MAX_PRIORITY)
        self._add_event('DISCONNECTED_EVENT', _MAX_PRIORITY)
        self._add_event('CONNECT_REQUEST_EVENT', _DEFAULT_PRIORITY)
        self._add_event('DISCONNECT_REQUEST_EVENT', _DEFAULT_PRIORITY)
        self._add_event('TAKE_PICTURE_REQUEST_EVENT', _DEFAULT_PRIORITY)
        self._add_event('START_RECORDING_REQUEST_EVENT', _DEFAULT_PRIORITY)
        self._add_event('STOP_RECORDING_REQUEST_EVENT', _DEFAULT_PRIORITY)
        self._add_event('CONNECT_TIMEOUT_EVENT', _MAX_PRIORITY)
        self._add_event('DISCONNECT_TIMEOUT_EVENT', _MAX_PRIORITY)
        self._add_event('RECORDING_TIMEOUT_EVENT', _MAX_PRIORITY)
        return self.events

    def _set_up_timers(self):
        # redefine this to add/remove timeouts.
        self._add_timer('connecting', _CONNECT_TIMEOUT, 'CONNECT_TIMEOUT_EVENT')
        self._add_timer('disconnecting', _DISCONNECT_TIMEOUT, 'DISCONNECT_TIMEOUT_EVENT')
        self._add_timer('taking_pic', _TAKING_PIC_TIMEOUT, 'TAKING_PIC_TIMEOUT_EVENT')
        self._add_timer('recording', _DEFAULT_RECORD_TIME, 'RECORDING_TIMEOUT_EVENT')
        return self.timers

    def _set_up_interrupts(self):
        self.interrupts = {}
        return self.interrupts

    def _set_up_requests(self):
        self._add_request('CONNECT', 'CONNECT_REQUEST_EVENT')
        self._add_request('DISCONNECT', 'DISCONNECT_REQUEST_EVENT')
        self._add_request('TAKE_PICTURE', 'TAKE_PICTURE_REQUEST_EVENT')
        self._add_request('START_RECORDING', 'START_RECORDING_REQUEST_EVENT')
        self._add_request('STOP_RECORDING', 'STOP_RECORDING_REQUEST_EVENT')
        return self.requests

    # called from __init__().
    def _get_device_id(self, label):
        """
        See that sensor.
        :in: label (int) Unique id
        :out: id (str)
        """
        # 'sensor' if not redefined.
        return '-'.join(['cv2','camera',str(label)])

    def _set_video_path(self, timestamp_label):
        _video_extension = 'avi'        # avi, mp4
        self._video_path = '.'.join([
            '_'.join([
                self._base_path+timestamp_label,
                str(self)]), _video_extension])
    
    def _set_picture_path(self, timestamp_label):
        _picture_extension = 'jpg'      # png, jpg
        self._picture_path = '.'.join([
            '_'.join([
                self._base_path+timestamp_label,
                str(self)]), _picture_extension])

    def _set_data_paths(self, timestamp_label):
        self._set_video_path(timestamp_label)
        self._set_picture_path(timestamp_label)

    def _fill_info(self):
        """
        Chat up the device to find where it lives as well
          as how to get into its front door.
        :in: old_info {dict} - any old metadata 'bout the device.
        :out: info {dict}
        """
        # TODO
        try:
            super()._fill_info()
        except:
            super(CV2_Camera, self)._fill_info()
        _cv2_camera_info = {
                'class': 'cv2-camera',
                'resolution': {
                    'width': str(self._resolution['width']),
                    'height': str(self._resolution['height'])
                    },
                'frame_rate': str(self._f_frames)
                }
        self.info.update(_cv2_camera_info)

    def _set_up_daemon(self):
        _initial_state = 'SLEEPING'
        state_handlers = [
                ('SLEEPING', self._sleep),
                ('CONNECTING', self._connect),
                ('STANDING_BY', self._idle),
                ('RECORDING', self._record),
                ('TAKING_PICTURE', self._snap),
                ('DISCONNECTING', self._disconnect)
                ]
        for state, handler in state_handlers:
            self.add_state(state, handler)
        self.set_up(start_state=_initial_state)
        
    # more even redefinedment.
    def _set_record_time(self, duration):
        _duration = float(duration)
        self.record_time = _duration
        self._set_timer('recording', _duration)

    def _link_comms(self):
        """
        thread to build a bridge  ) 0 o .with a camera.
        """
        self.channel = cv2.VideoCapture(int(self.address))
        if self.channel and self.channel.isOpened():
            self.printf('Connected')
            self.connected.value = 1

    def _break_comms(self):
        self.channel.release()
        if not self.channel.isOpened():
            self.printf('Disconnected')
            self.connected.value = 0

    def _test_comms(self):
        # test communications with device; DAEMON.
        if self.connected.value > 0:
            if self.state == 'CONNECTING':
                self._post_event('CONNECTED_EVENT')
        elif self.connected.value == 0:
            if self.state == 'DISCONNECTING':
                self._post_event('DISCONNECTED_EVENT')

    
    # FEATURES af.
    def _take_picture(self):
        """
        Take a single picture.
        """
        self.streaming.value = 1
        timestamp_label = self._check_wrist('label')
        self._set_picture_path(timestamp_label)
        while(1<2):
            ret, frame = self.channel.read()
            if ret:
                self.printf('hi nub')
                cv2.imwrite(self._picture_path, frame)
            break
        self.streaming.value = 0

    def _test_photo(self):
        # see if the picture is done been tekked.
        if self.streaming.value > 0:
            time.sleep(0.3)
        else:
            self._post_event('COMPLETE_EVENT')
            

    def _display_preview(self):
        ret, frame = self.channel.read()
        if ret:
            cv2.imshow('-'.join([
                'preview',
                str(self)]), frame)
            time.sleep(2)       # TODO : <-- make ui.
        cv2.destroyAllWindows()
    
    def _record_video(self):
        # TODO : make some setters.
        this_resolution = (
                self._resolution['width'],
                self._resolution['height'])  # <-- Change resolution here.
        w = self.channel.get(3)     #1280 [default]
        h = self.channel.get(4)     #720 [default]
        # TODO: test if this can be written to after being released.
        # set paths for recording video.
        timestamp_label = self._check_wrist('label')
        self._set_metadata_path(timestamp_label)
        self._set_video_path(timestamp_label)
        out = cv2.VideoWriter(self._video_path, self._fourcc, self._f_frames, (int(w), int(h)))
        while self.streaming.value > 0:
            timestamp = self._check_wrist('timestamp')
            try:
                ret, frame = self.channel.read()
                if ret:
                    # TODO : build service out.
    #                cv2.imshow('-'.join([
    #                    'preview',
    #                    str(self)]), frame)
                    out.write(frame)
            except:
                continue
        cv2.destroyAllWindows()
        # NOTE : can only post events from the main thread yo.


    # Device-level state machine.
    def _preview(self, this_event):
        # TODO
        pass

    def _snap(self, this_event):
        """
        Snarpshort.
        """
        if this_event == 'INIT_EVENT':
            self.printf('Say cheeze')
            self._start_timer('taking_pic')
            self._start_process(self._take_picture, 'SNAPPER')
        elif this_event == 'PICTURE_TIMEOUT_EVENT':
            self.printf('Timed out taking picture! Disconnecting')
            self._next_state = 'DISCONNECTING'
        elif this_event == 'COMPLETE_EVENT':
            self.printf('(:')
            self.generate_metadata()
            self._next_state = 'STANDING_BY'
        else:
            self._test_photo()
            time.sleep(0.3)

    def _record(self, this_event):
        """
        From device to file.
        """
        if this_event == 'INIT_EVENT':
            self.streaming.value = 1    # set streaming to 'on'.
            self.printf('Recording : '+str(self.channel)+' for '+str(self.record_time))
            if self.record_time > 0.0:     # if timer unset, stream indefinitely.
                self._start_timer('recording')
            self._start_thread(self._record_video, 'RECORDER')
        elif this_event == 'RECORDING_TIMEOUT_EVENT' or this_event == 'STOP_RECORDING_REQUEST_EVENT':
            self.streaming.value = 0    # set streaming to 'off'
            self.printf('Recording complete')
            self.generate_metadata()
            self._next_state = 'STANDING_BY'
        else:
            time.sleep(0.3)

    def _idle(self, this_event):
        if this_event == 'INIT_EVENT':
            self.printf('Standing by')
        elif this_event == 'START_RECORDING_REQUEST_EVENT':
            self._next_state = 'RECORDING'
        elif this_event == 'TAKE_PICTURE_REQUEST_EVENT':
            self._next_state = 'TAKING_PICTURE'
        elif this_event == 'DISCONNECT_REQUEST_EVENT':
            self._next_state = 'DISCONNECTING'
        else:
            time.sleep(0.1)

#    def _connect(self, this_event):
#        """
#        Connecting.
#        """
#        # init : attempt to connect, start timeout.
#        if this_event == 'INIT_EVENT':
#            self.printf('Connecting')
#            self._start_timer('connecting')     # <-- adjust this timeout for fine tuning.
#        elif this_event == 'CONNECT_TIMEOUT_EVENT':
#            self._next_state = 'SLEEPING'
#        elif this_event == 'CONNECTED_EVENT':
#            self._kill_processes()      # wait for connection process to terminate.
#            self.channel = self._shared_space_queue.get()
#            self._next_state = 'STANDING_BY'
#        elif this_event == 'DISCONNECT_REQUEST_EVENT':
#            self._next_state = 'DISCONNECTING'
#        else:
#            time.sleep(0.3)
#            self._test_comms()
#            time.sleep(0.3)
#
#    def _disconnect(self, this_event):
#        if this_event == 'INIT_EVENT':
#            self.printf('Disco nnecting...')
#            self._shared_space_queue.put(self.channel)
#            self._start_timer('disconnecting')
#            self._start_process(self._break_comms, 'DISCONNECTOR')
#        elif this_event == 'DISCONNECTED_EVENT':
#            self._kill_processes()      # wait for connection process to terminate.
#            self.channel = self._shared_space_queue.get()
#            self._next_state = 'SLEEPING'
#        elif this_event == 'DISCONNECT_TIMEOUT_EVENT':
#            say('Channel clogged; cannot disconnect', 'error')
#            self._next_state = 'SLEEPING'
#        else:
#            time.sleep(0.3)
#            self._test_comms()
#            time.sleep(0.3)
#
#
    def start_recording(self, duration=0.0):
        """
        Turn it on.
        :in: duration (float) streaming time [s]; duration <= 0.0 == continuous streaming!!
        """
        # TODO: add state check.
        self._set_record_time(duration)
        self._incoming_requests.put((_DEFAULT_PRIORITY, 'START_RECORDING'))

    def stop_recording(self):
        """
        Turn it off.
        """
        # TODO: add state check.
        self._incoming_requests.put((_DEFAULT_PRIORITY, 'STOP_RECORDING'))

    def take_picture(self):
        """
        Camera-specific.
        """
        # TODO: add state check.
        self._incoming_requests.put((_DEFAULT_PRIORITY, 'TAKE_PICTURE'))
        print('Wow, put request into queue : '+str(self))
        self._wait_for_('TAKING_PICTURE')
        print('WOWO, taking pic... : '+str(self))


def __test__cv2_camera():
    cv2_cameras = find_cv2_cameras()
    try:
        for cv2_camera in cv2_cameras:
            cv2_camera.connect()
            # start a pool of processes.
        time.sleep(3)
        for cv2_camera in cv2_cameras:
            if not cv2_camera.state == 'STANDING_BY':
                print('Deleting camera '+str(cv2_camera))
                cv2_camera.disconnect()
                cv2_cameras.remove(cv2_camera)
                del cv2_camera
        while 1<2:
#            for cv2_camera in cv2_cameras:
#                cv2_camera.start_recording()
#            time.sleep(5)
#            for cv2_camera in cv2_cameras:
#                cv2_camera.stop_recording()
#            for cv2_camera in cv2_cameras:
#                cv2_camera._wait_for_('STANDING_BY')
            print('Now trying to take a pic')
            for cv2_camera in cv2_cameras:
                cv2_camera.take_picture()
            time.sleep(2)
    except KeyboardInterrupt:
        for cv2_camera in cv2_cameras:
            cv2_camera.disconnect()

if __name__ == '__main__':
    __test__cv2_camera()
