import datetime
import csv
from tqdm import tqdm
import os

def write_csv(samples: dict, out_folder=".") -> str:
    sample_columns = ['GOS timestamp', 'GTR timestamp', 'Current Weight',
                    'Sensor 1', 'Sensor 2', 'Sensor 3', 'Sensor 4',
                    'Sensor 5', 'Sensor 6', 'Sensor 7', 'Sensor 8']
    date_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    file_name = os.path.join(out_folder, f'{date_time}_gator_data.csv')
    try:
        with open(file=file_name, mode='w', encoding='utf-8', newline='') as csv_file:
            csv_writer = csv.DictWriter(csv_file, sample_columns)
            csv_writer.writeheader()
            for sample in tqdm(samples, desc='Writing samples', unit='row'):
                csv_writer.writerow(sample)
    # if the user runs out of disk space...
    except IOError:
        print("Error: could not write to file. Make sure you have enough disk space. Don't worry - your drain is still in memory - just free up enough space and press ENTER to try again.")
        input("Press ENTER to try again...")
        return write_csv(samples)
    return file_name