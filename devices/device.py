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
    import queue
    from .squawk import say
except:
    import Queue as queue
    from squawk import say


## Global declarations or something.
_LOWEST_PRIORITY = 2
_EPOCH = datetime.datetime(1970,1,1)
_DEVICE_STATES = [
        'sleeping',
        'connecting',
        'standing_by']

_SUPPORT_TABLE = {
        'interface': [
            'serial',
            'i2c'],
        'device_type': [
            'usb_camera',
            'pi_camera']}
_TIMER_RESET = (False, 0.0)
_TIMERS_MAX = 8                             # Number of available timers / device.
_TIMERS_INIT = [_TIMER_RESET]*_TIMERS_MAX     # Reset state for all timers.
_EVENT_QUEUE_MAX_SIZE = 8                   # Max number of entries in the event queue.

## Local functions.
def _get_time_now(time_format='utc'):
    """
    Thanks Jon.  (;
    :in: time_format (str) ['utc','epoch']
    :out: timestamp (str)
    """
    if time_format == 'utc' or time_format == 'label':
        return datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    elif time_format == 'epoch' or time_format == 'timestamp':
        td = datetime.datetime.utcnow() - _EPOCH
        return str(td.total_seconds())
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
        :in: label (int) Unique ID
        :in: address
        :in: interface
        """
        global _TIMERS_INIT, _EVENT_QUEUE_MAX_SIZE
        self._supported_events = [
                'no_event',
                'connected',
                'disconnected',
                'connect_received',
                'disconnect_received',
                'timeout_0',
                'timeout_1',
                'timeout_2',
                'timeout_3',
                'timeout_4',
                'timeout_5',
                'timeout_6',
                'timeout_7']
        self._supported_states = [
                'sleeping',
                'connecting',
                'standing_by']
        self.address = str(address)
        self.interface = interface
        self.id = self._get_device_id(label)
        self.base_path = './test_data/'
        self.file_extension = 'txt'
        # Set file path to buffer path.
        self.file_path = '.'.join([
            '_'.join([
                self.base_path+'buffer',
                self.id]),
            self.file_extension])

        self.info = {}
        self.event_queue = queue.PriorityQueue(maxsize=_EVENT_QUEUE_MAX_SIZE)
        self.active_threads = []
        self.active_processes = []
        self.active_timers = _TIMERS_INIT

        self.migrate_state('sleeping')
        self._start_thread(self._run, 'daemon')

    def __str__(self):
        try:
            return str(self.id)
        except:
            return 'device'

    # Toolbelt.
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
            return process
        return None

    def _start_thread(self, target, name, args=(), kwargs={}):
        """
        Get them wheels turning.
        :in: target (*funk)
        :in: name (str) NOTE : set as daemon process with the word 'daemon' in here.
        :in: args (*)
        :in: kwargs {*}
        :out: thread (Thread)
        """
        thread = threading.Thread(target=target, name=name, args=args, kwargs=kwargs)
        if (name.find('daemon')) != -1:
            thread.daemon = True
        thread.start()
        if thread.isAlive():
            self.active_threads.append(thread)
            return thread
        return None

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

    def _remove_old_threads(self):
        """
        Clean self.active_threads.
        """
        for thread in self.active_threads:
            if not thread.isAlive():
                self.active_threads.remove(thread)

    def _remove_old_processes(self):
        """
        Clean self.active_processes.
        """
        for process in self.active_processes:
            if not process.is_alive():
                self.active_processes.remove(process)

    def _countdown(self, timer_num, duration):
        """
        Counting down the HH:MM:SS.
        """
        global _TIMER_RESET
        time_left = duration
        start_time = float(_get_time_now('epoch'))
        self.active_timers[timer_num] = (True, time_left)
        while time_left > 0:
            current_time = float(_get_time_now('epoch'))
            time_left = current_time - start_time
        self.active_timers[timer_num] = _TIMER_RESET

    def _get_timer_info(self, timer_num):
        """
        :in: timer_num (int)
        :out: timer_active, time_left (Bool, float)
        """
        try:
            return self.active_timers[timer_num]
        except:
            say('Invalid timer number: '+str(timer_num), 'error')
            return (False, -1.0)

    def _set_timer(self, timer_num, duration):
        """
        :in: timer_num (int) [0 -> _TIMER_MAX-1]
        :in: duration (float) [seconds]
        """
        timer_active, time_left = self._get_timer_info(timer_num)
        if timer_active or time_left < 0:
            say('Cannot set timeout for timer '+str(timer_num), 'warning')
        say('Timeout : '+str(duration)+'s')
        self._start_thread(self._countdown, 'timeout', args=[timer_num, duration])

    def _reset_timers(self):
        """
        Reset timers.
        """
        global _TIMERS_INIT
        self._active_timers = _TIMERS_INIT

    def migrate_state(self, n_state):
        """
        :in: n_state (str) next state
        """
        # TODO: Make this more beefy if needed.
        self.state = n_state
        self._post_event((0, 'init'))
        self._reset_timers()

    # Device-level state machine.
    def _peek_event(self):
        """
        :out: priority, event (int, str)
        """
        priority, event = self.event_queue.get_nowait()
        self.event_queue.put(priority, event)
        return priority, event

    def _post_event(self, (priority, event)):
        """
        :in: priority, event (int, str)
        """
        # TODO: implement as a priority queue.
#        global _LOWEST_PRIORITY
#        print('Priority '+str(priority)+' (lowest '+str(_LOWEST_PRIORITY)+'); Event '+str(event))
#        priority_max, event_max = self._get_event() # TODO: make this suck less.
#        while priority > priority_max:
#            priority_max, event_max = self._get_event() # TODO: make this suck less.
        self.event_queue.put((priority, event))

    def _get_event(self):
        """
        Check for new events.
        :out: event (str)
        """
        global _LOWEST_PRIORITY
        if not self.event_queue.empty():
            priority, event = self.event_queue.get_nowait()
            return priority, event
        else:
            return _LOWEST_PRIORITY, 'no_event'

    def _sleep(self, this_event):
        """
        Sleeping.
        """
        say('sleeping')
        
    def _connect(self, this_event):
        """
        Connecting.
        """
        say('connecting')

    def _stand_by(self, this_event):
        """
        Standing by.
        """
        say('standing by')

    def _update(self):
        """
        Check for inputs.
        """
        for index, timer in enumerate(self.active_timers):
            if timer[0] and timer[1] < 0:
                event = 'timeout_'+str(index)
                priority = 0
                self._post_event((priority, event))
            self._remove_old_threads()
            self._remove_old_processes()

    def _run(self):
        """
        Check for events, update state broh.
        """
        try:
            while True:
                this_event = self._get_event()
                if self.state == 'sleeping':
                    self._sleep(this_event)
                elif self.state == 'connecting':
                    self._connect(this_event)
                elif self.state == 'standing_by':
                    self._stand_by(this_event)
                else:
                    say('Out of state and in '+str(self.state), 'error')
                self._update()
        except KeyboardInterrupt:
            raise

    # Datatype definitions.
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

    def _link_comms(self):
        return 'Hi nub.'

    def _connect(self):
        """
        Change state here.
        """
        success = False
        timeout = 10.0      # <-- Edit connection timeout / attempt here.
        self.migrate_state('connecting')
        attempt = 1
        self.channel = self._link_comms()
        _timer = self._start_thread(self._countdown, 'connecting', (timeout))
        while 1<2:
            # Only return success if connection confirmed.
            if self._test_connection():
                self.migrate_state('standing_by')
                success = True
                break
            # Try again if the timer expires.
            if not _timer.is_alive():
                self._disconnect()
                attempt += 1
                if attempt > attempts:
                    say('Failed to connect to '+str(self), 'error')
                    self.migrate_state('sleeping')
                    break
                self._start_thread(self._link_comms, 'connecting')
                _timer = self._start_thread(self._countdown, 'connecting', (timeout))
            time.sleep(0.1)
        return success
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
        Change state here.
        """
        raise NotImplementedError

    def _test_connection(self, options={}):
        """
        <placeholder>
        """
        raise NotImplementedError

    def set_file_path(self, path_base='./test_data/'):
        """
        Set the base of the output path for data flow.
        :in: path_base (str) working directory [default]
        """
        if not os.path.isdir(path_base):
            say('Creating '+path_base)
#            try:
            os.mkdir(path_base)
#            except:
#                say(''.join([
#                        'Could not create directory at ',
#                        path_base,
#                        '; using default directory']),
#                    'warning')
#                path_base = './test_data/'
        self.base_path = path_base
        timestamp_label = _get_time_now('label')
        self.file_path = '.'.join([
            '_'.join([
                self.base_path+timestamp_label,
                self.id]),
            self.file_extension])

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
            * file_extension (str) txt [default]
        :out: success (Bool)
        """
        # TODO: Add options currently supported.
        timeout = 10.0
        self.connected = False
        self._fill_info()
        attempts = 1
        self.migrate_state('connecting')
        self._start_thread(self._connect, 'connecting')
        while 1<2:
            if self.state == 'connecting':
                break
            time.sleep(0.3)
        return True

    def clean_up(self):
        """
        Close down shop.
        """
        self._post_event((1, 'disconnect_received'))
        self._kill_threads()
        self._kill_processes()
        self._disconnect()
        self.migrate_state('sleeping')
        return True

