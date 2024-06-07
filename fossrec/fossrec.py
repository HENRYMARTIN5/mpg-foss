
# region Globals
BUCKET_WEIGHT = 1.80  # lbs
USE_TARE = False      # set to True if you haven't already tared the scale
DEFAULT_PORT = "COM7" # default port for the scale - if this isn't found, the script will ask for a port
LOG_SCALE = True      # log scale data to console
LOG_GATOR = False     # log gator data to console
CHECK_ADMIN = False
SKIP_GATOR_CHECK = True # for faster debugging
# endregion

from photonfirst.gator_api import GatorApi
import serial
from serial.tools import list_ports
import string
import threading
import re
import datetime
import pandas as pd

def cog_int_to_wavelength(val: int) -> float:
    return 1514+((val * (1586-1514))/(2 ** 18)) # magic formula from the gator datasheet

print("Initializing scale...")
print("Available ports:")
for port in list_ports.comports():
    print("\t" + port.device)
if not DEFAULT_PORT in [port.device for port in list_ports.comports()]:
    print(f"Default port {DEFAULT_PORT} not found. What port should we use?")
    DEFAULT_PORT = input(" -> ")
print(f"Opening serial port {DEFAULT_PORT}...")
ser = serial.Serial(DEFAULT_PORT, 9600, timeout=1)
print("Serial port opened.")

print("Initializing Gator...")
api = GatorApi()
try:
    gator = api.get_gators()[0]
except IndexError:
    raise Exception("Plug in the Gator and **TURN IT ON** before running this script.")
assert gator is not None
if not SKIP_GATOR_CHECK:
    print("Fetching settings from Gator to make sure it's alive...")
    settings = {
        "f Factor": gator.get_ffactor(),
        "COG Threshold": gator.get_cogthreshold(),
        "Sample freq.": gator.get_samplefrequency()
    }
    print("Found Gator! Settings:")
    for k, v in settings.items():
        print(f"  {k}: {v}")

def convert_sample_to_wavelength(sample):
    return {
        "Sensor 1": cog_int_to_wavelength(sample["Sensor 1"]),
        "Sensor 2": cog_int_to_wavelength(sample["Sensor 2"]),
        "Sensor 3": cog_int_to_wavelength(sample["Sensor 3"]),
        "Sensor 4": cog_int_to_wavelength(sample["Sensor 4"]),
        "Sensor 5": cog_int_to_wavelength(sample["Sensor 5"]),
        "Sensor 6": cog_int_to_wavelength(sample["Sensor 6"]),
        "Sensor 7": cog_int_to_wavelength(sample["Sensor 7"]),
        "Sensor 8": cog_int_to_wavelength(sample["Sensor 8"])
    }

# HACK: extra charmap to fix the encoding issues with the scale
extra_charmap = {
    b"\xa0": b"\x20", # space
    b"\xb0": b"\x30", # 0
    b"\xb1": b"\x31", # 1
    b"\xb2": b"\x32", # 2
    b"\xb3": b"\x33", # 3
    b"\xb4": b"\x34", # 4
    b"\xb5": b"\x35", # 5
    b"\xb6": b"\x36", # 6
    b"\xb7": b"\x37", # 7
    b"\xb8": b"\x38", # 8
    b"\xb9": b"\x39", # 9
}

current_weight = 0.0
buffer = ""
pattern = re.compile(r'\d{1,3}\.\d{2}(?:lb|l)') # compile once, better performance - why wasn't I doing this before??
thread_running = True
thread_initialized = False
start_seconds = datetime.datetime.now().timestamp()

f = open("fossrec.csv", "w")
f.write("elapsed_time,weight,wavelength 1,wavelength 2,wavelength 3,wavelength 4,wavelength 5,wavelength 6,wavelength 7,wavelength 8\n")

def gator_stream(sample):
    global collected_data, current_weight
    sample = convert_sample_to_wavelength(sample)
    if LOG_GATOR:
        print(sample)
    frame = [datetime.datetime.now().timestamp() - start_seconds, current_weight, *convert_sample_to_wavelength(sample).values()]
    f.write(",".join(map(str, frame)) + "\n")

def decode_ascii_with_extra(data: bytes) -> str:
    # HACK: really stupid way to layer the extra encoding... but it works and minimizes the error rate
    dot_point = data.find(b".")
    if dot_point < 3:
        return ""
    for char in extra_charmap:
        data = data.replace(char, extra_charmap[char])
    return data.decode("ascii", errors="ignore")

def filter_printable(s):
    return ''.join(filter(lambda x: x in string.printable, s))

def remove_all(s, chars):
    for c in chars:
        s = s.replace(c, "")
    return s

def read_scale() -> float:
    global current_weight, thread_t, thread_initialized, buffer
    r = ser.read_all()
    decoded = filter_printable(decode_ascii_with_extra(r))
    if decoded.strip() != "":
        buffer += decoded
        buffer = remove_all(buffer, "\r\n")
        matches = pattern.findall(buffer)
        if len(matches) > 0:
            buffer = ""
            weight = float(remove_all(matches[0], "lb"))
            current_weight = weight
            thread_initialized = True
            if LOG_SCALE:
                print(f"-> {'{:6.2f}'.format(weight)}lb")
            return weight
    return current_weight

running = True
def scale_thread():
    global running
    while running:
        try:
            read_scale()
        except Exception as e:
            print("Error in scale thread:", e)

gator.start_measurement_datastream(gator_stream)
t = threading.Thread(target=scale_thread)
t.start()
print("Measurement datastream started. Press Ctrl+C or Enter to stop.")
try:
    input()
except KeyboardInterrupt:
    gator.stop_measurement_datastream()
    running = False
    t.join()
    print("Measurement datastream stopped.")
print("Saving CSV...")
f.close()
running = False
print("CSV saved.")
print("If the program isn't exiting properly, it is now safe to kill it.")
exit(0)
