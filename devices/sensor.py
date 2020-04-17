"""
sensor.py - A pretty generic superclass for sensors.
sableye - sensor interface
Public:
    * Sensor(Device)
modified : 4/16/2020
  ) 0 o .
"""
try:
    from .device import Device, say
except:
    from device import Device, say

class Sensor(Device):
    """
    Your second one-stop-shop for sensor comms.
    """
    def __init__(self, address, interface):
        try:
            super().__init__(address, interface)
        finally:
            super(Sensor, self).__init__(address, interface)

    def _fill_info(self):
        """
        Chat up the device to find where it lives as well
          as how to get into its front door.
        :in: old_info {dict} - any old metadata 'bout the device.
        :out: info {dict}
        """
        try:
            super()._fill_info()
        finally:
            super(Sensor, self)._fill_info()
        self.info.update({'class': 'sensor'})
        

    def _stream(self):
        """
        <placeholder>
        """
        raise NotImplementedError

    def start_stream(self, options):
        """
        Open the stream.
        :in: options {dict}
        :out: success (Bool)
        """
        success = True
        self._start_thread(self._stream(), name='streaming')
        self.status = 'streaming'
        # TODO: Auto-generate logs of changes of state.
        return success

    def pause_stream(self, options):
        """
        Pause data stream.
        :in: options {dict}
        :out: success (Bool)
        """
        success = True
        self.status = 'idling'
        return success

    def stop_stream(self, options):
        """
        End data stream.
        :in: options {dict}
        :out: success (Bool)
        """
        success = True
        self.status = 'idling'
        return success
