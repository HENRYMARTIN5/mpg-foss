import argparse
import numpy as np
import pandas as pd
from dateutil.parser import parse
from betterlib.logging import Logger
np.random.seed(0)

logger = Logger("./nmpg-pre.log", "NMPG Preprocessor")

parser = argparse.ArgumentParser(description='Data pre-processing script for NMPG/MPG-FOSS')
parser.add_argument('microstrain', metavar='microstrain', type=str, help='Path to microstrain data')
parser.add_argument('weight', metavar='weight', type=str, help='Path to weight data')
parser.add_argument('output', metavar='output', type=str, help='Path to output file')
args = parser.parse_args()
logger.debug("parsed args")

def convert_to_timestamp(timestamp_str):
    try:
        parsed_timestamp = parse(timestamp_str)
        return str(parsed_timestamp)
    except ValueError as e:
        print(f"Error parsing the timestamp: {e}")
        return None

def unique_strings(array):
    return list(set(array))

logger.info("Microstrain file: " + args.microstrain)
logger.info("Weight file: " + args.weight)
logger.info("Output file: " + args.output)

logger.info("Loading microstrain data...")
microstrain = pd.read_csv(args.microstrain, delimiter=';', skiprows=3, parse_dates=True).values
logger.info("Loading weight data...")
weight = pd.read_csv(args.weight, delimiter=',', header=None).values
logger.info("Data loaded.")

logger.info("Pruning microstrain data...")
microstrain = microstrain[:, -8:] # last 8 columns are the only ones we care about

logger.info("Converting timestamps...")
microstrain[:, 0] = np.vectorize(convert_to_timestamp)(microstrain[:, 0])
weight[:, 1] = np.vectorize(convert_to_timestamp)(weight[:, 0])

# logger.info("Merging data...")
# indices = np.searchsorted(weight[:, 0], microstrain[:, 0])
# merged = np.hstack((microstrain, weight[indices, 1:]))
# logger.info("Data merged.")

logger.info("Taking FFTs...")
# FFTs for microstrain in 1-second windows, take average of each window for weight and match up
all_timestamps = 

logger.info("Saving data...")
np.savetxt(args.output, microstrain, delimiter=',', fmt='%s')
logger.info("Data saved.")