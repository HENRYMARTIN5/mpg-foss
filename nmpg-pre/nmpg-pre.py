import argparse
import numpy as np
import pandas as pd
from dateutil.parser import parse
from betterlib.logging import Logger
import os
from tqdm import tqdm
import json
import sys

np.random.seed(0)

logger = Logger("./nmpg-pre.log", "NMPG Preprocessor")

debug = True

def space(length: int) -> str:
    return " " * length

parser = argparse.ArgumentParser(description='Data pre-processing script for NMPG/MPG-FOSS')
parser.add_argument('data', metavar='data', type=str, help='Path to data (standard format: microstrain dir and weight_data.csv) - wavelength data will be converted to µstrain')
parser.add_argument('--indent', dest='indent', action='store_true', help='Export JSON with indentation')
parser.add_argument('--no-interact', dest='interact', action='store_false', help='Disable interactive mode (default: enabled)')
parser.add_argument('--no-frf', dest='frf', action='store_false', help='Disable FRF calculation for noise reduction (default: enabled)')
parser.add_argument('--match-method', dest='match_method', type=str, default='fixed', help='Method for matching timestamps (default: fixed) - options: fixed, timestamp-smart')
args = parser.parse_args()
logger.debug("parsed args")

def convert_to_timestamp(timestamp_str):
    try:
        parsed_timestamp = parse(timestamp_str)
        return str(parsed_timestamp)
    except ValueError as e:
        print(f"Error parsing timestamp: <{e}>")
        return None
    
microstrain_path = os.path.join(args.data, "microstrain")
weight_path = os.path.join(args.data, "weight_data.csv")
output_path = os.path.join(args.data, "processed_drain.json")

def unique_strings(array):
    return list(set(array))

def frf(x, y):
    return np.fft.fft(x) / np.fft.fft(y)

logger.info("Sorting microstrain data...")
microstrain_files = os.listdir(microstrain_path)
microstrain_files.sort()
logger.info("Merging microstrain data...")
new_data = """Channel 1; Sensor 1; Sensor 2; Sensor 3; Sensor 4; Sensor 5; Sensor 6; Sensor 7; Sensor 8

receive_ts; packet_ts; seqnr; sync status; TEC status; missed frames; channel; numsens; wavelength 1; wavelength 2; wavelength 3; wavelength 4; wavelength 5; wavelength 6; wavelength 7; wavelength 8
"""

is_microstrain = True

for file in microstrain_files:
    if "wavelength" in file.lower():
        is_microstrain = False
    print(f"Merging microstrain file {microstrain_files.index(file)+1}/{len(microstrain_files)}", end="\r")
    with open(os.path.join(microstrain_path, file), "r") as f:
        lines = f.readlines()
        new_data += "".join(lines[3:])
print()
logger.info("Microstrain data merged.")
logger.info("Saving...")
with open("./microstrain_joined.csv", "w") as f:
    f.write(new_data)

new_microstrain = "./microstrain_joined.csv"

logger.info("Microstrain file: " + new_microstrain)
logger.info("Weight file: " + weight_path)
logger.info("Output file: " + output_path)

logger.info("Loading microstrain data...")
microstrain = pd.read_csv(new_microstrain, delimiter=';', skiprows=3, parse_dates=True).values
logger.info("Loading weight data...")
weight = pd.read_csv(weight_path, delimiter=',', header=None, skiprows=1).values
logger.info("Data loaded.")

if not is_microstrain:
    logger.info("Converting wavelength data to µstrain...")
    # grab last 8 columns of wavelength data
    wavelength = microstrain[:, -8:]
    tracks = []
    microstrain_tracks = []
    for i in range(0,7):
        tracks.append(wavelength[:, i])
    for track in tracks:
        track = np.array(track, dtype=np.float64)
        track = track.reshape((len(track), 1))
        normalized_track = ((track[:, 0] - track[0, 0]) / track[0, 0]) * (1 / (1 - 0.22)) * 10**6 # magic formula for conversion - even I don't know how it works
        microstrain_tracks.append(normalized_track)
    microstrain_tracks = np.array(microstrain_tracks)
    # place the data back into the original array
    for i in range(0,7):
        microstrain[:, i+8] = microstrain_tracks[i]

logger.info("Converting timestamps...")
logger.debug("Calculating length...")
total = len(microstrain)
logger.debug(f"Length: {total}")
for i in tqdm(range(total), desc="Converting timestamps", unit="rows"):
    timestamp = convert_to_timestamp(microstrain[i, 0])
    microstrain[i, 0] = timestamp
logger.debug("Calculating length...")
total = len(weight)
logger.debug(f"Length: {total}")
for i in tqdm(range(total), desc="Converting timestamps", unit="rows"):
    print(f"Converting weight timestamps {i+1}/{total}", end="\r")
    timestamp = convert_to_timestamp(weight[i, 1])
    weight[i, 1] = timestamp
print()
logger.info("Timestamps converted.")

logger.info("Finding 0.2s intervals for FRFs...")
# find all timestamps that fall into 0.2s intervals, round to help with this
first_timestamp = microstrain[0, 0]
last_timestamp = microstrain[-1, 0]
logger.debug(f"First timestamp: {first_timestamp}")
logger.debug(f"Last timestamp: {last_timestamp}")
intervals = np.arange(parse(str(first_timestamp)), parse(str(last_timestamp)), pd.Timedelta("0.2s"))
# cut off last 5 characters of each timestamp to remove milliseconds
logger.info("Rounding timestamps...")
intervals = [str(i)[:-5] for i in intervals]

frfs = []
# format: [<timestamp>, data: [...], <weight average>]

if args.interact:
    logger.debug("Waiting for user choice...")
    inp = input("By default, this script takes FRFs from FBG 7 to FBG 2. If you don't know what this is, just ignore it. Do you want to change this? [y/N] ")
    if inp.lower() == "y":
        try:
            logger.debug("User chose to change FRFs.")
            logger.debug("Waiting for user input...")
            fbg1 = int(input("Enter the number of the sensor FBG to include: "))
            fbg2 = int(input("Enter the number of the correction FBG to include: "))
            logger.debug("User input received.")
        except ValueError:
            logger.error("Invalid input, using default 7 to 2.")
            fbg1 = 7
            fbg2 = 2
    else:
        logger.debug("User chose to use default FRFs.")
        fbg1 = 7
        fbg2 = 2
else:
    logger.debug("Interactive mode disabled, using default FRFs.")
    fbg1 = 7
    fbg2 = 2

logger.info("Starting FRF processing...")
startrow = 0
weight_startrow = 0
for i in tqdm(range(len(intervals)), desc="Processing FRFs", unit="intervals"):
    interval = intervals[i]
    data = []
    if args.match_method == "timestamp-smart":
        num_without_timestamp_match = 0
        timestamp_threshold = 16000
        for i in range(startrow, len(microstrain)):
            if microstrain[i, 0][0:-5].endswith(interval[-10:]):
                data.append(microstrain[i])
                startrow = i # speed gets exponentially better with this implemented
            else:
                num_without_timestamp_match += 1
                if num_without_timestamp_match > timestamp_threshold:
                    break
    elif args.match_method == "fixed":
        fixed_interval = 19320
        timestep = 0.2
        step = int(fixed_interval * timestep)
        for i in range(startrow, startrow + step):
            try:
                data.append(microstrain[i])
            except IndexError:
                break
        startrow += step
    # something similar but using the microstrain timestamp to find matches in the weight data
    found_something = False
    curr_interval = interval
    tries = 0
    weight_matches = []
    maxtries = 3
    while not found_something:
        tries += 1
        weight_matches = []
        for i in range(weight_startrow, len(weight)):
            row = weight[i]
            if row[1][0:-5].endswith(interval[-10:]):
                weight_matches.append(row)
                weight_startrow = i
        if len(weight_matches) > 0:
            found_something = True
            break
        if tries > maxtries:
            logger.debug("!!! No weight data for interval " + interval + " !!!")
            break
        # try incrementing the interval by 0.1s
        curr_interval = str(parse(curr_interval) + pd.Timedelta("0.1s"))
        if curr_interval.endswith("00000"):
            curr_interval = curr_interval[:-4]
    # calculate weight average
    if found_something:
        weight_avg = 0.0
        for match in weight_matches:
            weight_avg += match[0]
        try:
            weight_avg /= len(weight_matches)
        except ZeroDivisionError:
            logger.critical("It should be impossible to get here! Something has gone horribly wrong!")
            sys.exit(1)
    else:
        weight_avg = 0.0

    frf_x = []
    frf_y = []
    for row in data:
        frf_x.append(row[fbg1+7])
        frf_y.append(row[fbg2+7])
    frf_x = np.array(frf_x)
    frf_y = np.array(frf_y)
    try:
        if args.frf:
            result = frf(frf_x, frf_y)
        else:
            result = np.fft.fft(frf_x)
    except ValueError as e:
        result = np.array([0.0])
    frfs.append([interval, result, weight_avg])

newfrfs = []
for frf in frfs:
    newlist = frf[1].tolist()
    for i in range(len(newlist)):
        # convert complex numbers to real numbers
        newlist[i] = newlist[i].real
    newfrfs.append([frf[0], newlist, frf[2]])

frfs = newfrfs

logger.info("FRFs calculated.")
logger.info("Pruning zeros...")
newfrfs = []
for i in tqdm(range(len(frfs)), desc="Pruning zeros", unit="intervals"):
    _frf = frfs[i]
    if _frf[2] != 0:
        newfrfs.append(_frf)
frfs = newfrfs

logger.info("Saving data..." + space(100))
# save to json
with open(output_path, "w") as f:
    if args.indent:
        json.dump(frfs, f, indent=4)
    else:
        json.dump(frfs, f)
logger.info("Data saved.")

logger.info("Cleaning up...")
os.remove(new_microstrain)
logger.info("Cleanup complete.")

logger.info("Done.")