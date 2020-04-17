"""
device.py - A generic as HECK device superclass.
sableye - sensor interface
Public:
    * Device(object)
modified : 4/16/2020
  ) 0 o .
"""
import os, time, datetime, json, threading
import subprocess as sp
try:
    from .squawk import say
except:
    from squawk import say


## Global declarations or something.
_EPOCH = datetime.datetime(1970,1,1)
_DEVICE_STATES = [
        'sleeping']
_SUPPORT_TABLE = {
        'interface': [
            'opencv',
            'picamera',
            'serial',
            'i2c'],
        'device_type': [
            'usb_camera',
            'pi_camera']}


## Local functions.
def _get_time_now(time_format='utc'):
    """
    Thanks Jon.  (;
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
        #         you one layer of recursion! YOU HAVE BEEN WARNED.  ) 0 o .
        return _get_time_now(time_format='epoch')

def _check_supported(options):
    """
    Check if something is supported
    :in: options (dict)
    :out: supported (Bool)
    """
    supported = True
    global _SUPPORT_TABLE
    try:
        for option in options.keys():
            if options[option] not in _SUPPORT_TABLE[option]:
                supported = False
                break
        return supported
    finally:
        raise Exception


class Device(object):
    """
    Your one-stop-shop for device communications.
    """
    def __init__(self, address, interface):
        """
        To inherit:
            * redefine _query_info and _get_device_id appropriately.
            * call this __init__ from the child Device.
        :in: device_address
        :in: serial_number
        :in: device_type
        """
        assert(_check_supported({'interface': interface}))
        self.address = address
        self.interface = interface
        self.id = self._get_device_id()
        self.status = 'sleeping'
        self.base_path = './'

        self.info = {}
        self.active_threads = []
        self.active_processes = []

    def _fill_info(self):
        """
        Chat up the device to find where it lives as well
          as how to get into its front door.
        :in: old_info {dict} - any old metadata 'bout the device.
        """
        self.info = {
                'address': self.address,
                'interface': self.interface,
                'id': self.id
            }

    def _get_device_id(self):
        """
        Hunt down the device ID.
        :out: id (str)
        """
        # 'generic' if not redefined!
        return 'generic'
    def _connect(self):
        """
        <placeholder>
        """
        raise NotImplementedError
#        channel = None
#        try:
#            if self.interface == 'serial':
#                self.channel = Serial.serial(address)
#            elif interface == 'i2c':
#                channel = smbus.SMBus(address)
#            return channel
#        finally:
#            raise Exception

    def _disconnect(self):
        """
        <placeholder>
        """
        raise NotImplementedError

    def _test_connection(self, options={}):
        """
        <placeholder>
        """
        raise NotImplementedError

    def _start_process(self, target, options=[]):
        """
        Get them wheels turning.
        :in: target (*funk)
        :in: options [*]
        :out: process (*process)
        """
        return None

    def _start_thread(self, target, name, options=[]):
        """
        Get them wheels turning.
        :in: target (*funk)
        :in: options [*]
        :out: thread (*thread)
        """
        thread = threading.Thread(target, args=options, name=name)
        self.active_threads.append(thread)
        return thread

    def _kill_processes(self):
        return True

    def _kill_threads(self):
        for thread in self.active_threads:
            say(' '.join(['Waiting for',thread.name,'to terminate']))
            while(thread.is_alive()):
                time.sleep(0.1)
        return True

    def set_file_path(self, path_base):
        """
        Set the base of the output path for data flow.
        :in: path_base (str)
        """
        say('Setting base file path for '+self.id+' to '+path_base)
        if os.path.isdir(path_base):
          self.base_path = path_base
        else:
          say(''.join([
            'Cannot set path base to ',
            path_base,
            '; directory does not exist; using working directory']),
            'warning')
          self.base_path = './'

    def generate_metadata(self):
        """
        Output metadata as a .json dictionary.
        """
        say('Generating metadata for '+self.id)
        timestamp_label = _get_time_now('label')
        metadata_path = '_'.join([
            self.base_path+timestamp_label,
            self.id+'.json'])
        if os.path.isfile(metadata_path):
          say(''.join([
            'File ',
            metadata_path,
            ' exists; appending to file']),
            'warning')
        with open(metadata_path, 'w+') as md_p:
            md_p.write(json.dumps(
                self.info,
                sort_keys=True,
                indent=4))

    def set_up(self, options={}):
        """
        Setup a device.
        :in: options (dict) - Defined by specific device.
        :out: success (Bool)
        """
        # TODO: Add options currently supported.
        self._fill_info()
        self.channel = self._connect()
        if(_test_connection(options)):
            return True
        return False

    def clean_up(self):
        """
        Close down shop.
        """
        self.status = 'sleeping'
        return True



