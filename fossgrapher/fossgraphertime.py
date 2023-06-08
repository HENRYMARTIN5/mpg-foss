import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Read the data from the csv file
print("Loading data")
data = pd.read_csv('06_08_23Wavelength_data_2023_06_08T09.csv', sep=';', skiprows=3)

# now we have our data, let's start processing to plot it
# first, we need to get all the unique string timestamps in the data (1st column):
timestamps = data.iloc[:, 0].unique()

plotData = []

# now we need to get columns at indices 8-11 and plot them in 3d based on the timestamp:
for timestamp in timestamps:
    rows = data.loc[data.iloc[:, 0] == timestamp]
    cols = rows.iloc[:, 8:12]
    _plotData = []
    for col in cols:
        # get the fft of the column
        fft = np.fft.fft(cols[col])
        _plotData.append(fft)
    plotData.append(_plotData)

# now we have the data, let's plot it in 3d
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# now we need to plot the data
for i in range(len(plotData)):
    for j in range(len(plotData[i])):
        ax.plot([i]*len(plotData[i][j]), [j]*len(plotData[i][j]), plotData[i][j])

plt.show()
        

