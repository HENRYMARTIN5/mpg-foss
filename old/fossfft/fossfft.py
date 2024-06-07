import argparse
import numpy as np
from betterlib.logging import Logger

logger = Logger("./fossfft.log", "FOSS FFT")

parser = argparse.ArgumentParser(description='Run a FFT on a FOSS (fiber optic sensing system) data capture.')
parser.add_argument('input', metavar='input', type=str, nargs=1, help='Input file (csv)')
parser.add_argument('output', metavar='output', type=str, nargs=1, help='Output file (csv)')

args = parser.parse_args()
logger.debug("parsed args")
logger.info("Input file: " + args.input[0])
logger.info("Output file: " + args.output[0])

logger.info("Loading data...")
data = np.genfromtxt(args.input[0], delimiter=';', skip_header=3)
logger.info("Data loaded.")

ffts = []

for i in range(8, 12):
    logger.info("Calculating FFT for row " + str(i) + "...")
    ffts.append(np.fft.fft(data[:, i]))
    logger.info("FFT calculated for row " + str(i) + ".")
logger.info("All FFTs calculated.")

# put the data back

new_data = np.zeros((len(ffts[0]), 4))
for i in range(len(ffts)):
    new_data[:, i] = ffts[i]

np.savetxt(args.output[0], new_data, delimiter=',', header="FFT1,FFT2,FFT3,FFT4")