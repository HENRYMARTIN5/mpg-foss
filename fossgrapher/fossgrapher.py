import argparse
import numpy as np
import matplotlib.pyplot as plt
from betterlib.logging import Logger
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

logger = Logger("./fossg.log", "FOSS Grapher")

parser = argparse.ArgumentParser(description='Generate a graph of a FOSS (fiber optic sensing system) data capture.')
parser.add_argument('input', metavar='input', type=str, nargs=1, help='Input file (csv)')
parser.add_argument('output', metavar='output', type=str, nargs=1, help='Output file (png)')

args = parser.parse_args()

logger.debug("parsed args")
logger.info("Input file: " + args.input[0])
logger.info("Output file: " + args.output[0])

# reading the data is a bit weird, since there are 3 lines of header and the delimiter is a semicolon. otherwise, it's just a csv
logger.info("Loading data...")
data = np.genfromtxt(args.input[0], delimiter=';', skip_header=3)
logger.info("Data loaded.")

ffts = []
above_average_times = []  # List to store the times when a value is above the average for each line

for i in range(8, 12):
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
for i in range(len(ffts)):
    line, = plt.plot(np.abs(ffts[i]), label='Row {}'.format(i+8))
    mplcursors.cursor(line)

plt.xlabel('Frequency')
plt.ylabel('Amplitude')
plt.legend()
plt.grid(True)
plt.title('Fourier Transforms')
plt.ylim(0, 30)
plt.savefig(args.output[0])
logger.info("Graph saved, showing figure...")
thread = threading.Thread(target=plotJumperThread, args=(plt,))
thread.start()
plt.show()
threadRunning = False
thread.join()
logger.info("Done.")
