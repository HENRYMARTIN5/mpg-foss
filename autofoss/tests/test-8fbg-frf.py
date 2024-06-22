import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import csd, welch
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter.simpledialog import askstring
from scipy.interpolate import interp1d

# Hide the main tkinter window
Tk().withdraw()

# Select CSV file
filename = askopenfilename(filetypes=[("CSV files", "*.csv")])
if not filename:
    raise ValueError("No file selected")

# User input for start time (in seconds)
tStart = float(askstring("MPG-FOSS", "Enter the start time (in seconds):", initialvalue="0"))

# Read the CSV file into a DataFrame
data = pd.read_csv(filename)
print(data) # pandas trims the output so we can get a nice preview

# Extract track data from specific columns
trackW = data.iloc[:, 2]
tracks = [data.iloc[:, i] for i in range(3, 10) if i != 1]

print(trackW)
print(tracks[0:5])

# Convert COG wavelength to microstrain
tracks = [(track - track.iloc[0]) / track.iloc[0] * (1 / (1 - 0.22)) * 1e6 for track in tracks]

# Sample rate, time window, and frequency limits
fs = 19320  # samples/sec
T = 0.2  # 0.2 seconds
f1, f2 = 200, 5000  # frequency limits in Hz

winStartIdx = int(np.floor(tStart * fs)) + 1

# Number of windows based on user input and window size
nWindows = int(np.floor((len(tracks[0]) - winStartIdx + 1) / (fs * T)))

# Figure initialization
plt.figure(figsize=(20, 15))

EPSILON = 1e-10

print("--- length ---")
print(f"{len(tracks)} x {len(tracks[0])}")

# Iterate over all possible pairs of tracks
for i in range(7):
    for j in range(7):
        if i != j:
            H_sum = 0
            
            for w in range(nWindows):
                # Extract the windowed segments
                winStart = winStartIdx + w * int(fs * T)
                winEnd = winStart + int(fs * T)
                segment1 = tracks[i][winStart:winEnd]
                segment2 = tracks[j][winStart:winEnd]
                
                # Compute transfer function
                fVec, Pxy = csd(segment1, segment2, fs=fs, nperseg=len(segment1))
                _, Pxx = welch(segment1, fs=fs, nperseg=len(segment1))
                H = Pxy / (Pxx + EPSILON)
                
                # Sum the transfer functions
                H_sum += H
            
            # Average the transfer functions
            H_avg = H_sum / nWindows
            
            # Compute the magnitude
            H_mag = np.abs(H_avg)
            
            # Select indices for desired frequency range
            freqIndices = (fVec >= f1) & (fVec <= f2)
            
            # Plot the magnitude of the averaged transfer function
            plt.subplot(8, 8, i * 8 + j + 1)
            plt.plot(fVec[freqIndices], H_mag[freqIndices])
            plt.title(f'Track {i+1} to Track {j+1}')
            plt.xlabel('Frequency (Hz)')
            plt.ylabel('Magnitude (με / με)')

# Add a title at the top of the figure
plt.suptitle('MPG-FOSS Transmittance Functions', fontsize=14, fontweight='bold')
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()