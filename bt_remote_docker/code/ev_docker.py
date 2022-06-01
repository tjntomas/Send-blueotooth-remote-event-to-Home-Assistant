import evdev
import asyncio
import aiohttp
import json 
from os import walk
import logging
from logging import getLogger
import defs 

config = defs.params().parameters
print(config)

KEY_STATE             = ['up', 'down', 'hold']
DEVICE_INFO_LOG       = "Using device {} from {}{}."
DEVICE_INFO_NOT_FOUND = "Device {} not found."

# Since the remote does not send repeating keypresses for some keys, we implement our own reapeating keys function.
REPEATING_KEYS  = config['repeating_keys']
API_KEY         = config['ha_token']            # Long-lived access token for HA.
EVENT_NAME      = config['event_name']          # Name of event fired in HA.
API_ENDPOINT    = config['ha_url'] + EVENT_NAME # API event endpoint for HA.
REPEAT_DELAY    = config['repeat_delay']        # Delay in seconds for repeating keys.
WAIT            = config['initial_delay']       # Initial delay before repating keys start to repeat.
                                                # initial delay = REPEAT_DELAY x WAIT seconds.
DEBUG_MODE      = config['debug_mode']

HEADERS         = {'content-type': 'application/json','Authorization': 'Bearer {}'.format(API_KEY)}
CMD             = "cmd"
CMD_TYPE        = "cmd_type"
CMD_TYPE_DOWN   = "down"
EVENT           = "event"
DEV_PATH        = "/dev/input/"
state           = "up" # Initial state for the key_repeater function.



def find_device(device_name):
  _, _, filenames = next(walk(DEV_PATH))
  for input_device in filenames:
    if EVENT in input_device:
      device = evdev.InputDevice(DEV_PATH + input_device)
      print(device.name)
      if device.name == device_name:
        return input_device
  return ""

async def key_repeater(cmd, cmd_type, session):
    """ Function to send repeating keypresses for some buttons. """
    print("repeating", cmd)

    global state
    cnt = 0
    flag = False

    # Repeat keypress until the button is released.
    while state == CMD_TYPE_DOWN:
        # Wait a bit before starting repeating keypresses.
        if cnt > WAIT:
            # Prepare the payload for the HA event.
            payload = {CMD: cmd, CMD_TYPE: " " + state}
            # Fire the event in HA.
            resp = await session.post(API_ENDPOINT, data=json.dumps(payload), headers=HEADERS) 
            await resp.text()                 
        await asyncio.sleep(REPEAT_DELAY)
        cnt = cnt + 1

async def handle_events(device):
    """ Function to listen to peripheral device 
        events using the evdev module. """

    # Get exclusive access to the device.
    device.grab()
    log.info(device.name)
    global state
    task_exist = False
    # Create a context manager for async posting of events to HA.
    async with aiohttp.ClientSession() as session:

        # Create a context manager for reading evdev events.
        async for event in device.async_read_loop():
            # Only process keypress events.
            if event.type == evdev.ecodes.EV_KEY:

                # Get the event code and the event type.
                key_name = evdev.categorize(event).keycode
                cmd_type = KEY_STATE[evdev.categorize(event).keystate]

                # Prepare the event payload for HA.
                payload = {CMD: key_name, CMD_TYPE: cmd_type}

                # Fire the event in HA.
                resp = await session.post(API_ENDPOINT, data=json.dumps(payload), headers=HEADERS)
                await resp.text()
                if DEBUG_MODE:
                    log.info(payload)
                    log.info(device.name)      

                # Check if a repeating key was pressed.
                if key_name in REPEATING_KEYS and (cmd_type == CMD_TYPE_DOWN ):
                    state = cmd_type
                    # Start task to repeat keypress until the button is released.
                    task = loop.create_task(key_repeater(key_name, state, session))
                    task_exist = True
                else:
                    state = cmd_type
                    # Cancel the repeating task when the button is released.
                    if task_exist:
                        task.cancel()

    # Close the aiohttp session.
    await session.close()  

if __name__ == "__main__":
    # Setup logging.
    log = getLogger(__name__)
    logging.getLogger('asyncio').setLevel(logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG)

    devices = []
    
    # Find the device path for all devices and add to devices list.
    for name in config['devices']:
        path = find_device(name)
        if path != "":
            device = evdev.InputDevice(DEV_PATH + path)
            devices.append(device)
            log.info(DEVICE_INFO_LOG.format(name, DEV_PATH, path))
        else:
            log.info(DEVICE_INFO_NOT_FOUND.format(name))

    # Create handle_event tasks for all devices.
    for device in  devices:
        asyncio.ensure_future(handle_events(device))
    loop = asyncio.get_event_loop()
    loop.run_forever()
