from .plotter import Plotter
import matplotlib.pyplot as plt
import numpy.fft as fft
import numpy as np
from . import frf_lib

class BigOlFRFPlotter(Plotter):
    # plots one giant FRF averaging the FFTs all FBGs together (damn, that's a lot of F acronyms)
    def plot(self):
        df = self.df
        # 1. split data into 1s chunks
        chunks = []
        # second row is the time in seconds, just find all that share the same exact time and put them in a chunk
        for time, chunk in df.groupby("Elapsed"):
            chunks.append(chunk)
        print(f"Found {len(chunks)} chunks")
        # validate lengths of chunks
        chunk_lengths = [len(chunk) for chunk in chunks]
        if len(set(chunk_lengths)) != 1:
            raise ValueError(f"Chunk lengths are not all the same: {chunk_lengths}")

if __name__ == "__main__":
    import pandas as pd
    df = pd.read_csv("autofoss_20240621142958_drain.csv")
    BigOlFRFPlotter(df).plot()
    plt.show()