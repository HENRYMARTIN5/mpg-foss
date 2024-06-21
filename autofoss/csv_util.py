import datetime
import csv
from tqdm import tqdm
import os
import traceback

def write_csv(samples: dict, out_folder=".") -> str:
    os.makedirs(out_folder, exist_ok=True)
    sample_columns = ['Timestamp', 'Elapsed', 'Current Weight',
                    'Sensor 1', 'Sensor 2', 'Sensor 3', 'Sensor 4',
                    'Sensor 5', 'Sensor 6', 'Sensor 7', 'Sensor 8']
    date_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    file_name = os.path.join(out_folder, f'autofoss_{date_time}_drain.csv')
    try:
        with open(file=file_name, mode='w', encoding='utf-8', newline='') as csv_file:
            csv_writer = csv.DictWriter(csv_file, sample_columns)
            csv_writer.writeheader()
            for sample in tqdm(samples, desc='Writing samples', unit='row'):
                csv_writer.writerow(sample)
    # if the user runs out of disk space...
    except IOError:
        traceback.print_exc()
        print("Error: could not write to file. Make sure you have enough disk space. Don't worry - your drain is still in memory - just free up enough space and press ENTER to try again.")
        input("Press ENTER to try again...")
        return write_csv(samples, out_folder=out_folder)
    return file_name