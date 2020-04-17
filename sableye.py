"""
sableye_data_collect.py - Collect data from sableye's sensors.
Public:
    * sableye__find_devices()
    * sableye__set_up([Device])
    * sableye__record(Device, [options])
    * sableye__stream(Device, [options])
    * sableye__pause(Device, [options])
    * sableye__close(Device, [options])
modified: 3/6/2020
  ) 0 o .
"""
import os, sys, datetime, copy, json
# Maintain Python2 compatibility...FOOLISHLY.
try:
    from .devices.* import Camera
    from .squawk import ask, say
except:
    from devices.* import Camera
    from squawk import ask, say
#finally:
#    print('Error! File \'squawk\' not found! Aborting...')
#    sys.exit(1)


## Local functions.
def _save_file(contents, save_path, option='+'):
    """
    Try to save a file.
    :in: contents (str)
    :in: save_path (str)
    :in: option (str) - {+ [append], ? [query_to_overwrite], ! [overwrite]}
    """
    action = 'w'
    if os.path.isfile(save_path):
        if option == '?':
            if option == '+' or not ask('File '+save_path+' exists. Replace?', answer_type=bool):
                action += '+'
    with open(save_path, action) as fp_save:
        fp_save.write(contents)

def sableye__find_devices(options=[]):
    """
    Identify connected sableye-enabled devices.
    Reads from a separate configuration file:
        + indexed by name, provides communications
    """
    devices = []
    devices = _find_cameras()
    return devices


def sableye__shadow_claw():
    # Set duration in seconds.
    duration = 10
    devices = sableye__find_devices()
    for device in devices:
        say('Setting up '+str(device))
        sableye__set_up(devices)
        say(str(device)+' setup complete', 'success')
    for device in devices:
        sableye__stream(device)
        say('Streaming from '+str(device), 'success')
    say('Streaming for '+str(duration)+'s')
    time.sleep(duration)
    for device in devices:
        say('Pausing '+str(device))
        sableye__pause(device)
        say(str(device)+' paused', 'success')
    for device in devices:
        say('Closing '+str(device))
        sableye__stop(device)
        say(str(device)+' closed', 'success')
    say('Test complete', 'success')
    say('exiting')

if __name__ == '__main__':
    sableye__shadow_claw()
