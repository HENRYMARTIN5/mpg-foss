import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the CSV file into a pandas DataFrame
df = pd.read_csv('206_08_23Wavelength_data_2023_06_08T10_34_41.csv', delimiter=';', header=None, skiprows=3)

# Convert the 'receive_ts' column to datetime type
df[0] = pd.to_datetime(df[0], format='%d%b%YT%H%M%S.%f')

# Set the 'receive_ts' column as the index
df.set_index(0, inplace=True)

# for each second, take the fft of that second's sensor data
num_seconds = (df.index[-1] - df.index[0]).seconds
num_intervals = int(num_seconds / 1)
num_rows = int(df.shape[0] / num_intervals)
num_columns = df.shape[1]
fourier_transforms = np.zeros((num_columns, num_intervals))
for i in range(num_intervals):
    interval_data = df.iloc[i * num_rows:(i + 1) * num_rows, 8:]
    for j in range(num_columns - 8):
        fourier_transforms[j, i] = np.abs(np.fft.fft(interval_data.iloc[:, j]))

# Create a heatmap plot of the Fourier transforms
plt.imshow(np.abs(fourier_transforms.T), aspect='auto', cmap='hot')
plt.colorbar()
plt.xlabel('Time (1-second intervals)')
plt.ylabel('Sensor Columns')
plt.title('Fourier Transforms of Sensor Columns per Second')
plt.xticks(np.arange(0, num_intervals, 10), rotation=45)
plt.yticks(np.arange(0, df.shape[1] - 8), range(1, df.shape[1] - 7))
plt.show()
