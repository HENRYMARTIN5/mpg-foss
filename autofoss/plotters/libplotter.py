import numpy as np
from scipy import signal
import pandas as pd

class Plotter:
    def __init__(self, df: pd.DataFrame):
        self.df = df
    
    def plot(self):
        raise NotImplementedError("plot method not implemented in child class")
    
    def save(self, path):
        raise NotImplementedError("save method not implemented in child class")
    
    def show(self):
        raise NotImplementedError("show method not implemented in child class")

def track_to_microstrain(track):
    """
    Convert track data to microstrain.
    
    Parameters:
    - track: Track data (pandas Series).
    
    Returns:
    - track: Track data in microstrain.
    """
    return (track - track.iloc[0]) / track.iloc[0] * (1 / (1 - 0.22)) * 1e6


def tfestimate(segment1, segment2, fs):
    """
    Estimate the transfer function between two signals.
    
    Parameters:
    - segment1: Input signal (numpy array).
    - segment2: Output signal (numpy array).
    - fs: Sampling frequency.
    
    Returns:
    - H: Transfer function estimate.
    - fVec: Frequency vector.
    """
    segment1 = np.asarray(segment1)
    segment2 = np.asarray(segment2)
    fVec, Pxy = signal.csd(segment1, segment2, fs=fs, nperseg=256, noverlap=128)
    _, Pxx = signal.welch(segment1, fs=fs, nperseg=256, noverlap=128)
    H = Pxy / Pxx
    return H, fVec