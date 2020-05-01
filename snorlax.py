"""
snorlax.py - Quaff up that data.
modified : 5/1/2020
     ) 0 o .
"""
# Maintain Python2 compatibility...FOOLISHLY.
import sys, time, datetime, threading
try:
    import queue as Queue
    from .sableye import detect, set_up_, record_from_, take_picture_from_
    from .alakazam import sort
    from .squawk import ask, say
except:
    import Queue
    from sableye import detect, set_up_, record_from_, take_picture_from_
    from alakazam import sort
    from squawk import ask, say


## local important stuff.
# events and event generators.
# TODO : best way?
__SUPPORTED_EVENTS = [
        'NO_EVENT',
        'INIT_EVENT',
        'EXIT_EVENT',
        'COMPLETE_EVENT',
        'TIMEOUT_1_EVENT',
        'TIMEOUT_2_EVENT',
        'SCHEDULED_EVENT',
        'INTERRUPT_EVENT',
        'POKEFLUTE_EVENT'
        ]
EVENT_QUEUE = Queue.Queue()     # TODO : priority

__SUPPORTED_INTERRUPTS = []
INTERRUPT_QUEUE = Queue.Queue()

# setting priorities.
_HIGHEST_PRIORITY = 0
_LOWEST_PRIORITY = _HIGHEST_PRIORITY + 3
_DEFAULT_PRIORITY = _HIGHEST_PRIORITY + 1

# states.
[SLEEPING,
SETTING_UP,
CALIBRATING,
LUMBERING_ABOUT] = range(0,4)
CURRENT_STATE = SLEEPING    # Stay present
NEXT_STATE = SLEEPING       #  with eyes on the road.    ) 0 o .

# devices.
DEVICES = []

# metadata.
TEST_INFO = {
        'devices': {}
        }

# timers/timeouts (s).
_TIMER_RESET = (False, 0.0)
[_TIMER_1,
_TIMER_2] = range(0,2)
_TIMERS = [
        _TIMER_1,
        _TIMER_2]
_TIMERS_MAX = len(_TIMERS)                      # Number of available timers.
_TIMERS_INIT = [_TIMER_RESET]*_TIMERS_MAX       # Reset state for all timers.
ACTIVE_TIMERS = _TIMERS_INIT
_DEFAULT_TIMEOUT = 60
_SET_UP_TIMEOUT = _DEFAULT_TIMEOUT
_CALIBRATION_TIMEOUT = _DEFAULT_TIMEOUT

# other.
_ACTIVE_THREADS = []
_ACTIVE_PROCESSES = []
_EPOCH = datetime.datetime(1970,1,1)

## helpers.
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

def _start_thread(target, name, args=(), kwargs={}):
    """
    Get them wheels turning.
    :in: target (*funk)
    :in: name (str) NOTE : set as daemon process with the word 'daemon' in here.
    :in: args (*)
    :in: kwargs {*}
    :out: thread (Thread)
    """
    global _ACTIVE_THREADS
    thread = threading.Thread(target=target, name=name, args=args, kwargs=kwargs)
    if (name.find('daemon')) != -1:
        thread.daemon = True
    thread.start()
    if thread.isAlive():
        _ACTIVE_THREADS.append(thread)
        return thread
    return None

def _migrate_state(next_state):
    """
    But y even thoh?
    State will be changed if it needs to by the next round through.
    """
    global NEXT_STATE
    NEXT_STATE = next_state
    return

# timer stuff.
def _start_timer(timer_number, duration):
    """
    Counting down the HH:MM:SS.
    """
    global ACTIVE_TIMERS
    time_left = duration
    start_time = float(_get_time_now('epoch'))
    ACTIVE_TIMERS[timer_number] = (True, time_left)
    while time_left > 0:
        current_time = float(_get_time_now('epoch'))
        time_left = current_time - start_time
    ACTIVE_TIMERS[timer_number] = _TIMER_RESET

def _reset_timers():
    """
    Reset timers.
    """
    global ACTIVE_TIMERS
    ACTIVE_TIMERS = _TIMERS_INIT

def _get_timer_info( timer_num):
    """
    :in: timer_num (int)
    :out: timer_active, time_left (Bool, float)
    """
    try:
        return active_timers[timer_num]
    except:
        say('Invalid timer number: '+str(timer_num), 'error')
        return (False, -1.0)

def _set_timer(timer_number, duration):
    """
    :in: timer_number (int) [0 -> _TIMER_MAX-1]
    :in: duration (float) [seconds]
    """
    timer_active, time_left = _get_timer_info(timer_number)
    if timer_active or time_left < 0:
        say('Cannot set timeout for timer '+str(timer_number), 'warning')
    say('Timeout : '+str(duration)+'s')
    _start_thread(_start_timer, 'timeout-daemon', args=[timer_number, duration])


## event stuff.
def _get_event():
    global EVENT_QUEUE, _LOWEST_PRIORITY
    if EVENT_QUEUE.empty():
        return _LOWEST_PRIORITY, 'NO_EVENT'
    return EVENT_QUEUE.get_nowait()

def _post_event(priority, event_name):
    global EVENT_QUEUE
    event = priority, event_name
    EVENT_QUEUE.put_nowait(event)

def _clear_events():
    global EVENT_QUEUE
    while not EVENT_QUEUE.empty():
        _get_event()


## state machine
# NOTE : implement as a class?
# TODO : best way?
# meat of the machine.
def _build_test_info(connected_devices=[]):
    global TEST_INFO
    for device in connected_devices:
        TEST_INFO['devices'][str(device)] = 'hi nublette.'

def _start_set_up():
    """
    Find available devices, ask USER about test, connect to devices.
    """
    # TODO : merge DEVICES and TEST_INFO?
    global TEST_INFO, DEVICES
    DEVICES = detect()
    _build_test_info(connected_devices=DEVICES)
    set_up_(DEVICES)
    _post_event(_DEFAULT_PRIORITY, 'COMPLETE_EVENT')

def _start_calibration():
    # TODO : once devices are all added.
    say('SNORLAX : Calibration complete', 'success')
    _post_event(_DEFAULT_PRIORITY, 'COMPLETE_EVENT')

def _start_clean_up():
    """
    Gently disconnect from devices, ask USER for next moves.
    """
    clean_up_(DEVICES)
    # TODO : (while DEVICES.unclean: sleep mas)
    _post_event(_DEFAULT_PRIORITY, 'COMPLETE_EVENT')

def _hibernation():
    """
    Zzz...
    """
    prompt = 'SNORLAX : Wake with Pokeflute? [Press ENTER]'
    ask(prompt)
    _post_event(_HIGHEST_PRIORITY, 'POKEFLUTE_EVENT')

def _get_lumbering():
    while 1<2:
        prompt = 'SNORLAX : Collect data for 5s... [Press ENTER, or \'exit\' to quit]'
        response = ask(prompt)
        if not response == 'exit':
            take_picture_from_(DEVICES)
            continue
        _post_event(_DEFAULT_PRIORITY, 'EXIT_EVENT')
        break

def _handle_calendar():
    return

def _handle_interrupt():
    return

# actual machine.
def _check_schedule():
    return

def _check_interrupts():
    global INTERRUPT_
    return

def _check_devices():
    """
    Just make sure all is proper.
    """
    return

def _check_timers():
    for index, timer in enumerate(ACTIVE_TIMERS):
        if timer[0] and timer[1] < 0:
            event_name = '_'.join([
                'TIMEOUT',
                str(timer),
                'EVENT'])
            _post_event(_HIGHEST_PRIORITY, event_name)

def _update_state():
    global CURRENT_STATE, NEXT_STATE
    if NEXT_STATE != CURRENT_STATE:
        CURRENT_STATE = NEXT_STATE
        _clear_events()
        _reset_timers() # TODO : see if this is all gouda.
        _post_event(_HIGHEST_PRIORITY, 'INIT_EVENT')


def _update():
    _check_schedule()
    _check_interrupts()
    _check_devices()
    _check_timers()
    _update_state()

def _rest(new_event):
    """
    This needs USER attention to wake up.
    """
    if new_event[1] == 'INIT_EVENT':
        say('SNORLAX : Zzz...')
        _start_thread(_hibernation, 'hibernating-daemon')
    elif new_event[1] == 'POKEFLUTE_EVENT':
        _migrate_state(SETTING_UP)
    else:
        time.sleep(0.3)
    return

def _set_up(new_event):
    global DEVICES
    if new_event[1] == 'INIT_EVENT':
        _start_thread(_start_set_up, 'setting_up-daemon')
        _set_timer(_TIMER_1, _SET_UP_TIMEOUT)
    elif new_event[1] == 'COMPLETE_EVENT':
        _migrate_state(CALIBRATING)
    elif new_event[1] == 'TIMEOUT_1_EVENT':
        _migrate_state(CLEANING_UP)
    else:
        time.sleep(0.1)
    return

def _calibrate(new_event):
    if new_event[1] == 'INIT_EVENT':
        _start_thread(_start_calibration, 'calibrating-daemon')
        _set_timer(_TIMER_1, _CALIBRATION_TIMEOUT)
    elif new_event[1] == 'COMPLETE_EVENT':
        _migrate_state(LUMBERING_ABOUT)
    else:
        time.sleep(0.1)
    return

def _lumber_about(new_event):
    if new_event[1] == 'INIT_EVENT':
        _start_thread(_get_lumbering, 'lumbering-daemon')
    elif new_event[1] == 'SCHEDULED_EVENT':
        _start_thread(_handle_calendar, 'calendar-daemon')
    elif new_event[1] == 'INTERRUPT_EVENT':
        _start_thread(_handle_interrupt, 'interruption-daemon')     # TODO : make priorities of interrupts.
    elif new_event[1] == 'EXIT_EVENT':
        _migrate_state(CLEANING_UP)
    else:
        time.sleep(0.3)
    return

def _clean_up(new_event):
    if new_event[1] == 'INIT_EVENT':
        _start_thread(_start_clean_up, 'cleaning_up-daemon')
        _set_timer(_TIMER_1, _SET_UP_TIMEOUT)
    elif new_event[1] == 'COMPLETE_EVENT':
        _migrate_state(SLEEPING)
    else:
        time.sleep(0.1)
    return

def run(user_input):
    """
    Initialize and run test.
    """
    _migrate_state(SETTING_UP)    # Initial state is asleep.
    global CURRENT_STATE
    while 1<2:
        new_event = _get_event()
        if CURRENT_STATE == SLEEPING:
            _rest(new_event)
        elif CURRENT_STATE == SETTING_UP:
            _set_up(new_event)
        elif CURRENT_STATE == CALIBRATING:
            _calibrate(new_event)
        elif CURRENT_STATE == LUMBERING_ABOUT:
            _lumber_about(new_event)
        elif CURRENT_STATE == CLEANING_UP:
            _clean_up(new_event)
        else:
            _migrate_state(CLEANING_UP)
        _update()

def _sift_args():
    """
    Parse out USER arguments into a dictionary.
    :out: user_input {}
    """
    # TODO
    return {}

def snorlax():
    """
    This script manages device interactions and allows USER to define
        testing parameters.
    """
    user_input = _sift_args()
    try:
        run(user_input)
    except KeyboardInterrupt:
        say('SNORLAX : Wild Snorlax fainted!', 'success')
        sys.exit()

if __name__ == "__main__":
    snorlax()
