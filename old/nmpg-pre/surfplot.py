from betterlib.logging import Logger
import numpy as np
import matplotlib.pyplot as plt
import os
import json
import mplcursors
import argparse

logger = Logger("./nmpg-surfplot.log", "NMPG Data Surfplot")

parser = argparse.ArgumentParser(description='Data surfplot script for NMPG/MPG-FOSS')
parser.add_argument('data', metavar='data', type=str, help='Path to data (should already be processed, containing processed_drain.json)')
args = parser.parse_args()

logger.info("Loading data...")
path = os.path.join(args.data, "processed_drain.json")
with open(path, "r") as f:
    data = json.load(f)
logger.info("Data loaded.")

logger.info("Zero-padding data...")
_data = data
for row in _data:
    # chop off the last 50% of each row's 2nd column
    row[1] = row[1][:int(len(row[1])/2)]
largest = 0
for row in _data:
    if len(row[1]) > largest:
        largest = len(row[1])
for row in _data:
    while len(row[1]) < largest:
        row[1].append(0)
data = _data
logger.info("Data zero-padded.")

logger.info("Double-checking data...")
first = len(data[0][1])
for row in data:
    if len(row[1]) != first:
        logger.critical("Somehow, the data is not the same length. This is a bug.")
        exit(1)

logger.info("Plotting...")
# plot one slice of the data to see what it looks like

cur_slice = 0
plt.figure(figsize=(20, 10))
line = plt.plot(np.abs(data[cur_slice][1]), label='FRF on FBGs 2/7')
mplcursors.cursor(line)
# add extra text to the plot
plt.title("FRF on FBGs 2/7 - " + data[cur_slice][0] + " - " + str(data[cur_slice][2]) + "lbs")
plt.legend()
plt.show(block=False)

for i in range(cur_slice, len(data)):
    plt.title("FRF on FBGs 2/7 - " + data[i][0] + " - " + str(data[i][2]) + "lbs")
    line[0].set_ydata(np.abs(data[i][1]))
    plt.pause(0.05)
plt.close()

logger.info("Done.")