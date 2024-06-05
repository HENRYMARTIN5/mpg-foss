"""
fossrec.py: Record a complete FOSS drain, including weight data and wavelength data.

Requires the PhotonFirst Gator Python API to be installed. See the MPG-FOSS shared drive for a copy.

Also requires the scale to be configured with the correct drivers. Download and run Zadig and select libusbK or WinUSB for the scale (which shows up as "USB Serial" in the dropdown).

On the scale, set the following configuration options:
User -> COM2 -> Layout -> LFUULF
User -> COM2 -> Byte fmt -> 8N1
User -> COM2 -> Baudrt -> 9600
"""

# region Globals
BUCKET_WEIGHT = 1.80 # lbs
USE_TARE = False # set to True if you haven't already tared the scale
# endregion

# region Initialization
print("Loading modules...")
from photonfirst.gator_api import GatorApi
import usb.core
import usb.util
import sys
import threading
import pandas as pd
import datetime
import sys
import traceback
import re

print("Initializing scale...")
dev = usb.core.find(idVendor=0x1a86, idProduct=0x7523)
if dev is None:
    raise Exception("Plug in the scale before running this script.")
assert dev is not None
ep = dev[0].interfaces()[0].endpoints()[0]
i = dev[0].interfaces()[0].bInterfaceNumber
dev.reset()
if not sys.platform.startswith('win'):
    if dev.is_kernel_driver_active(i):
        try:
            dev.detach_kernel_driver(i)
        except usb.core.USBError as e:
            raise Exception("Failed to detatch kernel driver: %s" % str(e))
dev.set_configuration()
eaddr = ep.bEndpointAddress

print("Initializing Gator...")
api = GatorApi()
try:
    gator = api.get_gators()[0]
except IndexError:
    raise Exception("Plug in the Gator and **TURN IT ON** before running this script.")
assert gator is not None
print("Fetching settings from Gator to make sure it's alive...")
settings = {
    "f Factor": gator.get_ffactor(),
    "COG Threshold": gator.get_cogthreshold(),
    "Sample freq.": gator.get_samplefrequency()
}
print("Found Gator! Settings:")
for k, v in settings.items():
    print(f"  {k}: {v}")
# endregion

print("Creating dataframe...")
data = pd.DataFrame(columns=["elapsed_time", "timestamp", "weight"], index=None)
current_weight = 0.0
start_seconds = datetime.datetime.now().timestamp()
thread_running = True
thread_initialized = False

charmap = {
    0x18: '0',
    0x9e: '.'
}

def str_decode(r):
    res = ""
    for byte in r:
        if byte in charmap:
            res += charmap[byte]
        else:
            res += "?"

# region Threads and Handlers
def decode(r) -> float:
    global current_weight, thread_initialized
    r = bytearray(r)
    # HACK: lazy and stupid, but it works
    r = r.decode("ascii").replace(" ", "").replace("\n", "").replace("\r", "")
    if len(r) < 6:
        return None
    pattern = re.compile(r'\b\d{1,3}\.\d{2}(?:lb|l)\b')
    matches = pattern.findall(r)
    if len(matches) == 0:
        return None
    weight = matches[0].replace('l', '').replace('b', '')
    try:
        current_weight = float(weight) if not USE_TARE else float(weight) - BUCKET_WEIGHT
        print("Weight: %slb" % current_weight)
        thread_initialized = True # signal that data is being received and the Gator stream can start
        return current_weight
    except ValueError:
        traceback.print_exc()
        return None

def scale_thread():
    global thread_running
    while thread_running:
        try:
            decode(dev.read(eaddr, 10, timeout=1000))
        except usb.core.USBError as e:
            traceback.print_exc()

def gator_stream(sample):
    global thread_initialized
    if not thread_initialized:
        return # wait for the scale thread to start so we don't get desynced
    print(sample) # TODO: add sample data to the dataframe
    data.loc[len(data)] = [datetime.datetime.now().timestamp() - start_seconds, pd.Timestamp.now(), current_weight]
# endregion

# region Main
scale_thread = threading.Thread(target=scale_thread)
print("Trying to open Gator data stream...")
gator_stream = gator.start_measurement_datastream(gator_stream)
print("Starting scale thread...")
scale_thread.start()
input("Press ENTER at any point to stop recording.")
print("Stopping Gator data stream...")
gator.stop_measurement_datastream()
print("Stopping scale thread...")
thread_running = False
scale_thread.join()
print("Saving CSV...")
data.to_csv(f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_fossrec.csv")
print("Done!")
# endregion
