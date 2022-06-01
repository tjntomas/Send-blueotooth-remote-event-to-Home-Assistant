import evdev
from os import walk
import logging

_, _, filenames = next(walk("/dev/input/"))
for input_device in filenames:
    if 'event' in input_device:
        device = evdev.InputDevice("/dev/input/" + input_device)
        print(device.name, input_device)