"""
Script to take full recordings of drains. Logs data from the Gator and scale to a CSV file and automatically enables noise generation and the valve with the MX100TP.

Make sure the scale is at factory defaults, except for:
User -> COM1 -> Mode -> Continuous

Procedure:
1. Ensure the Gator, power supply, and scale are connected and turned on.
2. Run this script.
4. Press ENTER to stop recording once the tank drains.
5. The script will save the data to a CSV file in the current directory. This may take a while, so don't close the script until it's done.
"""

# region Globals
DEFAULT_PORT = "COM7" # default port for the scale - if this isn't found, the script will ask for a port
LOG_SCALE = True      # log scale data to console
LOG_GATOR = False     # log gator data to console
USE_AUTO_ON = True    # automatically turn on the power supply
AUTO_END = True       # automatically stop the script after the tank drains
WEIGHT_TIMEOUT = 8    # time in seconds before considering the tank drained
AUTO_REFILL = True    # automatically refill the tank after the script ends
BUCKET_WEIGHT = 3.65  # weight of the bucket when empty (with a bit of wiggle room) in lbs
# endregion

import csv
import datetime
import logging
from logging.handlers import RotatingFileHandler
import serial
from serial.tools import list_ports
import re
import string
import threading
from tqdm import tqdm

from msl.equipment import (
    EquipmentRecord,
    ConnectionRecord,
    Backend,
)

from gator_api.gator_api import GatorApi
from gator_api.gator_data import GatorData

if USE_AUTO_ON:
    record = EquipmentRecord(
        manufacturer='Aim-TTi',
        model='MX100TP',
        connection=ConnectionRecord(
            # address='TCP::192.168.1.70::9221',  # if using the LAN port
            address='COM9',  # if using the USB or RS232 port
            # address='Prologix::192.168.1.71::1234::6',  # if using a Prologix GPIB-ETHERNET Controller
            backend=Backend.MSL,
            timeout=10,
        )
    )
    tti = record.connect()

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
logger = logging.getLogger(__name__)
log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s:%(lineno)d %(message)s')
handler = RotatingFileHandler('photonfirst-api.log',
                                maxBytes=(5 * 1024 * 1024),  # 5 MB
                                backupCount=1)               # 2 logfiles (rotated)
handler.setFormatter(log_formatter)
logger.setLevel(logging.INFO)
logger.addHandler(handler)
api = GatorApi(logger)
api.set_gator_log_level(4)
gators = api.query_gators()
nr_of_gators = len(gators)
plural_postfix = "" if nr_of_gators == 1 else "s"
print(f'Found {nr_of_gators} gator{plural_postfix} on the system')
if nr_of_gators < 1:
    raise Exception("Plug in the Gator and **TURN IT ON** before running this script.")

api.connect(gators[0])
gator = gators[0]

def to_nm(sample):
    return sample/100000 # HACK: terrible conversion method but it works

def convert_sample(sample):
    global current_weight
    return {
        "GOS timestamp": sample["GOS timestamp"],
        "GTR timestamp": sample["GTR timestamp"],
        "Current Weight": current_weight,
        "Sensor 1": to_nm(sample["Sensor 1"]),
        "Sensor 2": to_nm(sample["Sensor 2"]),
        "Sensor 3": to_nm(sample["Sensor 3"]),
        "Sensor 4": to_nm(sample["Sensor 4"]),
        "Sensor 5": to_nm(sample["Sensor 5"]),
        "Sensor 6": to_nm(sample["Sensor 6"]),
        "Sensor 7": to_nm(sample["Sensor 7"]),
        "Sensor 8": to_nm(sample["Sensor 8"])
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
    global current_weight, thread_t, thread_initialized, buffer, last_weight_change
    r = ser.read_all()
    decoded = filter_printable(decode_ascii_with_extra(r))
    if decoded.strip() != "":
        buffer += decoded
        buffer = remove_all(buffer, "\r\n")
        matches = pattern.findall(buffer)
        if len(matches) > 0:
            buffer = ""
            weight = float(remove_all(matches[0], "lb"))
            if current_weight != weight:
                last_weight_change = datetime.datetime.now().timestamp()
            current_weight = weight
            thread_initialized = True
            if LOG_SCALE:
                print(f"-> {'{:6.2f}'.format(current_weight)}lb")
            return weight
    return current_weight

def scale_thread():
    global thread_running
    while thread_running:
        try:
            read_scale()
        except Exception as e:
            print("Error in scale thread:", e)

def on_sample_received(data_array):
    global thread_running, thread_initialized, last_weight_change
    for sample in data_array:
        if not thread_initialized:
            continue
        if AUTO_END and datetime.datetime.now().timestamp() - last_weight_change > WEIGHT_TIMEOUT:
            print(f"Tank seems to be drained - no weight changes in {datetime.datetime.now().timestamp() - last_weight_change} seconds, over threshold of {WEIGHT_TIMEOUT} seconds. Stopping...")
            thread_running = False
            return
        if LOG_GATOR:
            print(sample) # kills performance, but useful for debugging
        samples.append(convert_sample(sample))

current_weight = 0.0
last_weight_change = datetime.datetime.now().timestamp()
buffer = ""
samples = []
pattern = re.compile(r'\d{1,3}\.\d{2}(?:lb|l)') # compile once, better performance - why wasn't I doing this before??
thread_running = True
thread_initialized = False
start_seconds = datetime.datetime.now().timestamp()

running = True
while running:
    current_weight = 0.0
    last_weight_change = datetime.datetime.now().timestamp()
    buffer = ""
    samples = []
    thread_running = True
    thread_initialized = False
    start_seconds = datetime.datetime.now().timestamp()
    print('Streaming data to CSV file...')
    if USE_AUTO_ON:
        tti.turn_on(1)
        print("Noise generation turned on.")
    gator_data = GatorData(api, logger)
    gator_data.register_callback(on_sample_received)
    api.start_streaming(gator)
    gator_data.start_streaming()
    t = threading.Thread(target=scale_thread)
    t.start()
    if USE_AUTO_ON:
        tti.turn_on(3)
        print("Valve opened.")
    try:
        while thread_running:
            pass
    except KeyboardInterrupt:
        pass
    print('Streaming stopped. Processing remaining samples...')
    api.stop_streaming(gator)
    gator_data.stop_streaming()
    print('Processing finished, stopping scale thread...')
    thread_running = False
    t.join()
    print('Scale thread stopped.')
    if USE_AUTO_ON:
        tti.turn_off(1)
        print("Noise generation turned off.")
        tti.turn_off(3)
        print("Valve closed.")
    print('Writing samples to CSV...')
    sample_columns = ['GOS timestamp', 'GTR timestamp', 'Current Weight',
                        'Sensor 1', 'Sensor 2', 'Sensor 3', 'Sensor 4',
                        'Sensor 5', 'Sensor 6', 'Sensor 7', 'Sensor 8']
    date_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    file_name = f'{date_time}_gator_data.csv'
    with open(file=file_name, mode='w', encoding='utf-8', newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, sample_columns)
        csv_writer.writeheader()
        for sample in tqdm(samples, desc='Writing samples', unit='row'):
            csv_writer.writerow(sample)
    print(f'CSV file written: {file_name}')
    if not AUTO_REFILL:
        exit(0)
    print('Refilling tank...')
    tti.turn_on(2)
    print("Pump turned on.")
    print('Waiting for tank to refill...')
    i = 0
    while read_scale() > BUCKET_WEIGHT:
        i += 1
        if i % 10 == 0:
            print(f"-> {'{:6.2f}'.format(current_weight)}lb - Still refilling...")
    tti.turn_off(2)
    print("Pump turned off.")