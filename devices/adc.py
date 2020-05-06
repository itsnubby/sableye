"""
i2c_device.py - Wrap your I2C devices up nicely in Python.
Radish'n'bots, LLC
     ) 0 o .
    modified : 2/10/2020
"""
import sys
if sys.version_info[0] < 3:
    print('Alas! I2C unsupported with this Pi below Python3!  ) 0 o .')
    sys.exit(1)
import Adafruit_ADS1x15
#import board
#import busio
#i2c = busio.I2C(board.SCL, board.SDA)
#import adafruit_ads1x15.ads1115 as ADS
#from adafruit_ads1x15.analog_in import AnalogIn
## module-level variables.
# ADC stuff.
GAIN = 1

class ADS1115(Sensor):
    """
    Wrapper for ADS1115 ADC.
    """
    def __init__(self, label, address, interface='i2c'):
        try:
            super().__init__(label, address, interface)
        except:
            super(ADS1115, self).__init__(label, address, interface)

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
            super(ADS1115, self)._fill_info()
        self.info.update({'class': 'adc'})

    def _get_device_id(self, label):
        """
        See that sensor.
        :in: label (int) Unique id
        :out: id (str)
        """
        # 'sensor' if not redefined.
        return '-'.join(['ads1115',str(label)])

    def set_file_paths(self, path_base='./test_data/'):
        """
        Set the base path to use to direct output data flow.
        :in: path_base (str) working directory [default './test_data/']
        :out: new_path_base (str) 
        """
        _video_extension = 'avi'        # avi, mp4
        _picture_extension = 'jpg'      # png, jpg
        # Check that base directory exists.
        if not os.path.isdir(path_base):
            say('Creating '+path_base)
            os.mkdir(path_base)
        # Generate unique id a la timestamp.
        timestamp_label = _get_time_now('label')
        new_path_base = '_'.join([
                path_base+timestamp_label,
                self.id])
        self._video_path = '.'.join([
            new_path_base,
            _video_extension])
        self._picture_path = '.'.join([
            new_path_base,
            _picture_extension])

    def _test_sub_channel(self, sub_channel):
        """
        Make sure that sub channel can be read.
        """
        # TODO: add conditionals based on DEVICE_STATE.
        _prev_value = 0
        _reps_to_fail = 30      # How many times a read value is repeated before failing.
        _reps = 0               # Gimme some more reps.
        while 1<2:
            _value = 0
            #try:
            _value = self.channel.read_adc(sub_channel, gain=GAIN)
            #except:
            #    # TODO
            #    return False
            if _value != _prev_value:
                _reps += 1
                if _reps >= _reps_to_fail:
                    return False
            return True

    def _find_sub_channels(self):
        # TODO: build out Channel/SubChannel ADTs.
        self._sub_channels = []             # Clear sub-channels first.
            for sub_channel in range(4):
                if self._test_sub_channel(self, sub_channel):
                    self._sub_channels.append(sub_channel)

    def _open_connection(self):
        """
        Thread to build an I2C bridge.
        """
        # Attempt to connect to main channel.
        attempt = 1
        while self.state == 'connecting':
            self.ads = Adafruit_ADS1x15.ADS1115(self.address, self.bus)
            if self._test_connection():
                event = (0, 'connected')
                self._post_event(event)
                break
            say(str(self)+' : connection attempt '+str(attempt)+' failure', 'warning')
            attempt += 1

        # Find available ADC channels.
        self._find_sub_channels()
    
    def _test_connection(self):
        """
        Check yer I2C port.
        :out: available (Bool) is device ready for communication?
        """
        # TODO: make fully funky.
        for sub_channel in self._sub_channels:
            if self.channel.read_adc(sub_channel, gain=GAIN):
                return True
        return False

    ## state machine
    def wait_for_(self, state):
        """
        Wait for this to be in some state.
        :in: state (str)
        """
        while 1<2:
            if self.state == state:
                break

    def _run(self):
        """
        Check for events, update state broh.
        """
        while True:
            this_event = self._get_event()
            if self.state == 'sleeping':
                self._sleep(this_event)
            elif self.state == 'connecting':
                self._connect(this_event)
            elif self.state == 'standing_by':
                self._stand_by(this_event)
            elif self.state == 'streaming':
                self._stream(this_event)
            elif self.state == 'disconnecting':
                self._disconnect(this_event)
            else:
                say('Out of state, outta mind, and in '+str(self.state), 'error')
            self._update()

    def set_up(self,options={}):
        """
        Setup an ADC.
        :out: success (Bool)
        :in: options {}
        """
        if not self.state == 'sleeping':
            say('Attempting to set up an existing device.', 'warning')
        say('Setting up')
        event = (1, 'connect_received')
        self._post_event(event)

    def clean_up(self):
        """
        Close down shop.
        :out: success (Bool)
        """
        if not self.state == 'sleeping':
            say('Shutting down '+str(self))
            event = (1, 'disconnect_received')
            self._post_event(event)
        else:
            say('Already shut down', 'success')
        
            else:
                time.sleep(0.1)

    def start_recording(self, duration=0.0):
        """
        Turn it on.
        :in: duration (float) streaming time [s]; duration <= 0.0 == continuous streaming!!
        """
        # TODO: Add state check.
        if duration <= 0.0:
            self._stream_mode = 'continuous'
        else:
            self._stream_mode = 'timed'
            self._stream_duration = duration

        event = (1, 'stream_received')
        self._post_event(event)

    def stop_recording(self):
        """
        Turn it off.
        """
        # TODO: Add state check.
        event = (1, 'stop_received')
        self._post_event(event)


def test_adc():
    """
    Ensure that all systems are a big GO.    ) 0 o .
    """
    # Edit overall test duration (s):
    test_duration = 60
    # Edit sampling frequency (Hz):
    f_sample = 0.5
    _default_address = 0x48

    # Sample data from I2C sensors over the desired time frame.
    this_dude = ADS1115('nublord', 0x48)
    print(this_dude.channel.value, this_dude.channel.voltage)

if __name__ == '__main__':
    print('Under construction...  ) 0 o .')
    test_adc()
