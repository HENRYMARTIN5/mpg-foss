import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from common.cog import cog_to_wavelength
import argparse
import numpy as np
from betterlib.logging import Logger

logger = Logger("./converter.log", "Data Converter")

parser = argparse.ArgumentParser(description='Convert an unofficial FOSS (fiber optic sensing system) data capture to a format similar to the official data (or at least close enough to be graphed by the FOSS Grapher).')
parser.add_argument('input', metavar='input', type=str, nargs=1, help='Input file (csv)')
parser.add_argument('output', metavar='output', type=str, nargs=1, help='Output file (csv)')

args = parser.parse_args()

logger.debug("parsed args")
logger.info("Input file: " + args.input[0])
logger.info("Output file: " + args.output[0])

logger.info("Loading data...")
# load with strings as well, since we need to parse the sensor numbers
_data = np.genfromtxt(args.input[0], delimiter=',', skip_header=3, dtype=str)
logger.info("Data loaded.")

# since this is unofficially grabbed data, we need to do some preprocessing to get it into a format similar to the official data
data = np.zeros((_data.shape[0], 16))
# find all unique timestamps in the data
timestamps = np.unique(_data[:, 1])
logger.info("Found " + str(len(timestamps)) + " unique timestamps.")
new_packets = []
# for each timestamp, find all rows that have that timestamp and put them in the right place in the new_packets array
for timestamp in timestamps:
    rows = np.where(_data[:, 1] == timestamp)[0]
    new_packets.append({"timestamp": timestamp})
    for row in rows:
        if _data[row, 4] != 1:
            new_packets[-1]["sensor_0" + str(int(_data[row, 2].split("_")[1]))] = _data[row, 3]

# now we have a list of packets, each with a timestamp and 8 sensor values. we need to put them into the `data` array
i = 0
for packet in new_packets:
    try:
        data[i, 0] = packet["timestamp"]
    except ValueError:
        # missing timestamp, skip this packet
        continue
    for j in range(8):
        try:
            data[i, j+8] = str(cog_to_wavelength(packet["sensor_0" + str(j+1)]))
        except KeyError:
            data[i, j+8] = '0'
    i += 1

# trim off the extra rows since we don't know how many there were going to be initially
data = data[:i, :]

logger.info("Saving data...")
# add a header to the data, just like the official data
header = """Channel 1; Sensor 1; Sensor 2; Sensor 3; Sensor 4; Sensor 5; Sensor 6; Sensor 7; Sensor 8

receive_ts; packet_ts; seqnr; sync status; TEC status; missed frames; channel; numsens; wavelength 1; wavelength 2; wavelength 3; wavelength 4; wavelength 5; wavelength 6; wavelength 7; wavelength 8"""
np.savetxt(args.output[0], data, delimiter=';', header=header, fmt='%s',comments='')
logger.info("Data saved.")