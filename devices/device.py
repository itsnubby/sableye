"""
device.py - A generic as HECK device superclass.
sableye - sensor interface
Public:
    * Device(object)
modified : 4/17/2020
  ) 0 o .
"""
import os, time, datetime, json, threading, multiprocessing
import subprocess as sp
try:
    from .squawk import say
except:
    from squawk import say


## Global declarations or something.
_EPOCH = datetime.datetime(1970,1,1)
_DEVICE_STATES = [
        'sleeping',
        'standing_by']
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
    except:
        raise Exception


class Device(object):
    """
    Your one-stop-shop for device communications.
    """
    def __init__(self, label, address, interface):
        """
        To inherit:
            * redefine _fill_info and _get_device_id appropriately.
            * call this __init__ from the child Device.
        :in: device_address
        :in: serial_number
        :in: device_type
        :in: label (int) Unique ID
        """
        assert(_check_supported({'interface': interface}))
        self.address = address
        self.interface = interface
        self.id = self._get_device_id(label)
        self.status = 'sleeping'
        self.base_path = './'

        self.info = {}
        self.active_threads = []
        self.active_processes = []

    def __str__(self):
        try:
            return str(self.id)
        except:
            return 'device'

    def _start_process(self, target, name, args=(), kwargs={}):
        """
        Get them wheels turning.
        :in: target (*funk)
        :in: args (*)
        :in: kwargs {*}
        :out: success (Bool)
        """
        process = multiprocessing.Process(target=target, args=args, kwargs=kwargs)
        process.start()
        if process.is_alive():
            self.active_processes.append(process)
            return True
        return False

    def _start_thread(self, target, name, args=(), kwargs={}):
        """
        Get them wheels turning.
        :in: target (*funk)
        :in: args (*)
        :in: kwargs {*}
        :out: success (Bool)
        """
        thread = threading.Thread(target=target, name=name, args=args, kwargs=kwargs)
        thread.start()
        if thread.isAlive():
            self.active_threads.append(thread)
            return True
        return False

    def _kill_process(self):
        """
        Terminate all active processes broh.
        """
        _timeout = 15   # <-- Set thread termination timeout (s) here.
        _attempts = 2   # <-- Set number of attempts here.
        for attempt in range(1,_attempts+1):
            say(' '.join(['Attempt #',str(attempt),': waiting for',thread.name,'to terminate']))
            process.join([_timeout])
            if not process.is_alive():
                say(' '.join([process.name,'terminated']), 'success')
                self.active_processes.remove(process)
                return True
        return False

    def _kill_processes(self):
        """
        Terminate all active processes broh.
        """
        while len(self.active_processes) > 0:
            for process in self.active_processes:
                if not self._kill_process(process):
                    continue
        return True

    def _kill_thread(self, thread):
        """
        Terminate a thread.
        :in: thread (*Thread)
        :out: success (Bool)
        """
        _timeout = 15   # <-- Set thread termination timeout (s) here.
        _attempts = 2   # <-- Set number of attempts here.
        for attempt in range(1,_attempts+1):
            say(' '.join(['Attempt #',str(attempt),': waiting for',thread.name,'to terminate']))
            thread.join([_timeout])
            if not thread.isAlive():
                say(' '.join([thread.name,'terminated']), 'success')
                self.active_threads.remove(thread)
                return True
        return False

    def _kill_threads(self):
        """
        Terminate all active threads broh.
        """
        while len(self.active_threads) > 0:
            for thread in self.active_threads:
                if not self._kill_thread(thread):
                    continue
        return True

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

    def _get_device_id(self, label):
        """
        Hunt down the device ID.
        :in: label (int) Unique ID
        :out: id (str)
        """
        # 'generic' if not redefined!
        return '-'.join(['generic',str(label)])

    def _connect(self):
        """
        Change status here.
        """
        self.status = 'standing_by'
#        channel = None
#        try:
#            if self.interface == 'serial':
#                self.channel = Serial.serial(address)
#            elif interface == 'i2c':
#                channel = smbus.SMBus(address)
#            return channel
#        except:
#            raise Exception

    def _disconnect(self):
        """
        Change status here.
        """
        self.status = 'sleeping'

    def _test_connection(self, options={}):
        """
        <placeholder>
        """
        raise NotImplementedError

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
        self.connected = False
        self._fill_info()
        self._connect()
        try:
            attempts_max = options['attempts']
        except:
            attempts_max = 5
        attempt_num = 1
        while attempt_num < attempts_max:
            if self._test_connection():
                self.connected = True
                break
            say(''.join([
                    str(self),
                    ' : Connection attempt#',
                    str(attempt_num),
                    ' failed']),
                'warning')
            attempt_num += 1
            time.sleep(0.3)

    def clean_up(self):
        """
        Close down shop.
        """
        self._kill_threads()
        self._kill_processes()
        self._disconnect()
        self.status = 'sleeping'
        return True

