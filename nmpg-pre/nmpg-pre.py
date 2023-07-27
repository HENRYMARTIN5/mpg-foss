import argparse
import numpy as np
import pandas as pd
from dateutil.parser import parse
from betterlib.logging import Logger
import time
import os
np.random.seed(0)

logger = Logger("./nmpg-pre.log", "NMPG Preprocessor")

parser = argparse.ArgumentParser(description='Data pre-processing script for NMPG/MPG-FOSS')
parser.add_argument('microstrain', metavar='microstrain', type=str, help='Path to microstrain data')
parser.add_argument('weight', metavar='weight', type=str, help='Path to weight data (directory, parts will be combined)')
parser.add_argument('output', metavar='output', type=str, help='Path to output file')
args = parser.parse_args()
logger.debug("parsed args")

def convert_to_timestamp(timestamp_str):
    try:
        parsed_timestamp = parse(timestamp_str)
        return str(parsed_timestamp)
    except ValueError as e:
        print(f"Error parsing timestamp: <{e}>")
        return None

def unique_strings(array):
    return list(set(array))

def frf(x, y):
    return np.fft.fft(x) / np.fft.fft(y)

logger.info("Sorting microstrain data...")
microstrain_files = os.listdir(args.microstrain)
microstrain_files.sort()
logger.info("Merging microstrain data...")
new_data = """Channel 1; Sensor 1; Sensor 2; Sensor 3; Sensor 4; Sensor 5; Sensor 6; Sensor 7; Sensor 8

receive_ts; packet_ts; seqnr; sync status; TEC status; missed frames; channel; numsens; wavelength 1; wavelength 2; wavelength 3; wavelength 4; wavelength 5; wavelength 6; wavelength 7; wavelength 8
"""
for file in microstrain_files:
    print(f"Merging microstrain file {microstrain_files.index(file)+1}/{len(microstrain_files)}", end="\r")
    with open(os.path.join(args.microstrain, file), "r") as f:
        lines = f.readlines()
        new_data += "".join(lines[3:])
print()
logger.info("Microstrain data merged.")
logger.info("Saving...")
with open("./microstrain_joined.csv", "w") as f:
    f.write(new_data)

new_microstrain = "./microstrain_joined.csv"

logger.info("Microstrain file: " + new_microstrain)
logger.info("Weight file: " + args.weight)
logger.info("Output file: " + args.output)

logger.info("Loading microstrain data...")
microstrain = pd.read_csv(new_microstrain, delimiter=';', skiprows=3, parse_dates=True).values
logger.info("Loading weight data...")
weight = pd.read_csv(args.weight, delimiter=',', header=None).values
logger.info("Data loaded.")

logger.info("Converting timestamps...")
logger.debug("Calculating length...")
total = len(microstrain)
logger.debug(f"Length: {total}")
start_time = time.time()
time_remaining = "unknown"
for i in range(total):
    print(f"Converting microstrain timestamps {i+1}/{total} - ETA: {time_remaining} {' '*30}", end="\r")
    timestamp = convert_to_timestamp(microstrain[i, 0])
    microstrain[i, 0] = timestamp
    if i % 10000 == 0:
        time_sofar = time.time() - start_time
        start_time = time.time()
        try:
            time_remaining = str(pd.Timedelta(seconds=(total - i) * time_sofar / i))
        except ZeroDivisionError:
            time_remaining = "unknown"
print()
logger.debug("Calculating length...")
total = len(weight)
logger.debug(f"Length: {total}")
for i in range(total):
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
intervals = np.arange(parse(first_timestamp), parse(last_timestamp), pd.Timedelta("0.2s"))
# cut off last 5 characters of each timestamp to remove milliseconds
logger.info("Rounding timestamps...")
intervals = [str(i)[:-5] for i in intervals]

frfs = []
# format: [<timestamp>, data: [...], <weight average>]

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

logger.debug("Calculating length...")
total = len(intervals)
logger.debug(f"Length: {total}")
logger.info("Starting FRF processing...")
for interval in intervals:
    print(f"Processing interval {interval} ({intervals.index(interval)+1}/{total}) - this is slow, so be patient (finding microstrain matches)                     ", end="\r") 
    data = []
    i = 0
    for row in microstrain:
        if row[0][0:-5].endswith(interval[-10:]):
            data.append(row)
            microstrain = np.delete(microstrain, np.where(microstrain[:, 0] == row[0]), axis=0)
        if i > 100000:
            break # lots of padding, but it still makes it faster than it was
        i += 1

    print(f"Processing interval {interval} ({intervals.index(interval)+1}/{total}) - this is slow, so be patient (calculating frf on {len(data)} data points)      ", end="\r")
    frf_x = []
    frf_y = []
    for row in data:
        frf_x.append(row[fbg1+7])
        frf_y.append(row[fbg2+7])
    frf_x = np.array(frf_x)
    frf_y = np.array(frf_y)
    result = frf(frf_x, frf_y)
    frfs.append([interval, result, 0.0]) # TODO: weight pairing

longest = 0
for frf in frfs:
    if len(frf[1]) > longest:
        longest = len(frf[1])
for frf in frfs:
    if len(frf[1]) < longest:
        frf[1] = np.pad(frf[1], (0, longest - len(frf[1])))

# logger.info("Merging data...")
# indices = np.searchsorted(weight[:, 0], microstrain[:, 0])
# merged = np.hstack((microstrain, weight[indices, 1:]))
# logger.info("Data merged.")

logger.info("Saving data...")
np.savetxt(args.output, frfs, delimiter=',', fmt='%s')
logger.info("Data saved.")