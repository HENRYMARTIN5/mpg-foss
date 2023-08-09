import argparse
from betterlib.logging import Logger
import os
from tqdm import tqdm
import json
import sys

logger = Logger("./nmpg-pre-bulk.log", "NMPG Preprocessor (Bulk Mode)")

debug = True


parser = argparse.ArgumentParser(description='Data pre-processing script for NMPG/MPG-FOSS')
parser.add_argument('data', metavar='data', type=str, help='Path to data (standard format: microstrain dir and weight_data.csv)')
parser.add_argument('--indent', dest='indent', action='store_true', help='Export JSON with indentation')
args = parser.parse_args()
logger.debug("parsed args")

dirs = os.listdir(args.data)
dirs.sort()

for i in tqdm(range(len(dirs)), desc="Preprocessing data...", unit="drains"):
    os.system("python3 nmpg-pre/nmpg-pre.py \"" + os.path.join(args.data, dirs[i]) + "\" --no-interact " + ("--indent" if args.indent else ""))
    logger.info("Preprocessed drain " + str(i+1) + "/" + str(len(dirs)) + " (" + dirs[i] + ")")

logger.info("Preprocessing complete.")