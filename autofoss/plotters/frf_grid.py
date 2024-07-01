from .libplotter import Plotter, tfestimate, track_to_microstrain
import matplotlib.pyplot as plt
from tkinter.simpledialog import askstring
import numpy as np

class FRFGridPlotter(Plotter):
    def __init__(self, df):
        super().__init__(df)
        self.fs = 19320              # samples/sec
        self.T = 0.2                 # 0.2 seconds
        self.f1, self.f2 = 200, 5000 # frequency limits in Hz
        self.EPSILON = 1e-10         # for numerical stability
        self.trackWIdx = 2           # column index of weight track
        self.tracksRange = (3, 10)   # column indices of COG tracks
    
    def plot(self):
        tStart = float(askstring("MPG-FOSS", "Enter the start time (in seconds):", initialvalue="0"))
        trackW = self.df.iloc[:, self.trackWIdx]
        tracks = [self.df.iloc[:, i] for i in range(*self.tracksRange) if i != self.trackWIdx]
        tracks = [track_to_microstrain(track) for track in tracks]
        winStartIdx = int(np.floor(tStart * self.fs)) + 1
        nWindows = int(np.floor((len(tracks[0]) - winStartIdx + 1) / (self.fs * self.T)))
        plt.figure(figsize=(20, 15))
        loop_amt = self.tracksRange[1] - self.tracksRange[0]
        for i in range(loop_amt):
            for j in range(loop_amt):
                if i != j:
                    H_sum = 0
                    for w in range(nWindows):
                        winStart = winStartIdx + w * int(self.fs * self.T)
                        segment1 = tracks[i][winStart:winStart + int(self.fs * self.T)]
                        segment2 = tracks[j][winStart:winStart + int(self.fs * self.T)]
                        H, fVec = tfestimate(segment1, segment2, self.fs)
                        H_sum += H
                    H_avg = H_sum / nWindows
                    H_mag = np.abs(H_avg)
                    freqIndices = (fVec >= self.f1) & (fVec <= self.f2)
                    plt.subplot(loop_amt, loop_amt, i * loop_amt + j + 1)
                    plt.plot(fVec[freqIndices], H_mag[freqIndices])
                    plt.title(f'Track {i+1} to Track {j+1}')
                    plt.xlabel('Frequency (Hz)')
                    plt.ylabel('Magnitude (με / με)')
        plt.suptitle('MPG-FOSS Transmittance Functions', fontsize=14, fontweight='bold')
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    def show(self):
        plt.show()
    
    def save(self, path):
        plt.savefig(path)