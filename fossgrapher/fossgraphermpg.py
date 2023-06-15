# modified to work with unofficially grabbed FOSS data, specifically from the original mpg-foss repo

import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from common.cog import cog_to_wavelength
import argparse
import numpy as np
import matplotlib.pyplot as plt
from betterlib.logging import Logger
import matplotlib.ticker as ticker
import threading
import mplcursors

threadRunning = True
def plotJumperThread(plt):
    global threadRunning
    while threadRunning:
        try:
            to = input("Jump to (q to quit): ")
            if to == 'q':
                threadRunning = False
                return
            to = int(to)
            plt.xlim(to-100, to+100)
            plt.ylim(0, 30)
        except ValueError:
            print("Invalid input. Try again.")
        except KeyboardInterrupt:
            threadRunning = False
            return

logger = Logger("./fossg-mpg.log", "MPG-FOSS Grapher")

parser = argparse.ArgumentParser(description='Generate a graph of a FOSS (fiber optic sensing system) data capture.')
parser.add_argument('input', metavar='input', type=str, nargs=1, help='Input file (csv)')
parser.add_argument('output', metavar='output', type=str, nargs=1, help='Output file (png)')
parser.add_argument("-n", "--no-fourier", help="Don't calculate the Fourier transforms - just plot raw data from each sensor", action="store_true")

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

ffts = []
above_average_times = []  # List to store the times when a value is above the average for each line

if not args.no_fourier:
    for i in range(12, 16):
        logger.info("Calculating FFT for row " + str(i) + "...")
        ffts.append(np.fft.fft(data[:, i]))
        avg = np.mean(data[:, i])
        above_avg_indices = np.where(data[:, i] > avg)[0]
        above_average_times.append(above_avg_indices)
        # now sort the above average times by the ones that are the most above average
        above_average_times[i-8] = sorted(above_average_times[i-8], key=lambda x: data[x, i] - avg, reverse=True)
        logger.info("Above average times calculated for row " + str(i) + ": " + str(above_average_times[i-8][:10]))
        logger.info("FFT calculated for row " + str(i) + ".")
    logger.info("All FFTs calculated.")

# Plotting the Fourier transforms
plt.figure()
if not args.no_fourier:
    for i in range(len(ffts)):
        line, = plt.plot(np.abs(ffts[i]), label='Sensor on r{}'.format(i+8))
        mplcursors.cursor(line)
else:
    for i in range(12, 16):
        line, = plt.plot(data[:, i], label='Sensor on r{}'.format(i))
        mplcursors.cursor(line)
if not args.no_fourier:
    plt.xlabel('Frequency')
    plt.ylabel('Amplitude')
else:
    plt.xlabel('Time')
    plt.ylabel('Value')
plt.legend()
plt.grid(True)
if not args.no_fourier:
    plt.title('Fourier Transforms')
else:
    plt.title('Raw Data')
if not args.no_fourier:
    plt.ylim(0, 30)
plt.savefig(args.output[0])
logger.info("Graph saved, showing figure...")
thread = threading.Thread(target=plotJumperThread, args=(plt,))
thread.start()
plt.show()
threadRunning = False
thread.join()
logger.info("Done.")
