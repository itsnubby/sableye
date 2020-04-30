"""
snorlax.py - Quaff up that data.
modified : 4/29/2020
     ) 0 o .
"""
# Maintain Python2 compatibility...FOOLISHLY.
try:
    import queue as Queue
    from .sableye import find_devices, USB_Camera
    from .alakazam import sort
    from .squawk import ask, say
except:
    import Queue
    from sableye import find_devices, USB_Camera
    from alakazam import sort
    from squawk import ask, say


## local important stuff.
# events and event generators.
# TODO : best way?
NO_EVENT, 
TIMEOUT_0,
TIMEOUT_1 = range(0,3)
EVENTS = [NO_EVENT, TIMEOUT_0, TIMEOUT_1]
_LOWEST_PRIORITY = len(EVENTS)

EVENT_QUEUE = Queue.Queue()     # TODO : priority


def _get_event():
    global EVENT_QUEUE, _LOWEST_PRIORITY
    if EVENT_QUEUE.empty():
        return _LOWEST_PRIORITY, NO_EVENT
    return _LOWEST_PRIORITY, NO_EVENT

def _post_event():


# state machine
# NOTE : implement as a class?
# TODO : best way?
SLEEPING,
SETTING_UP,
IDLING_ABOUT,
DOING_STUFF = range(0,4)

CURRENT_STATE = SLEEPING

def _migrate_state(next_state):
    global CURRENT_STATE
    CURRENT_STATE = next_state

def _rest(new_event):
    # Technically not necessary...
    _migrate_state(SETTNG_UP)

def run(user_input):
    """
    Initialize and run test.
    """
    global CURRENT_STATE
    while 1<2:
        new_event = _get_event()
        if CURRENT_STATE == SLEEPING:
            _rest(new_event)
        elif CURRENT_STATE == SETTING_UP:
            _set_up(new_event)
        elif CURRENT_STATE == IDLING_ABOUT:
            _idle_about(new_event)
        elif CURRENT_STATE == DOING_STUFF:
            _do_stuff(new_event)
        else:
            _migrate_state(SLEEPING)
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
    run(user_input)

if __name__ == "__main__":
    snorlax()
