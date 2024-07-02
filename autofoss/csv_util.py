import datetime
import csv
from tqdm import tqdm
import os
import traceback

def bytes_to_gb(size: int) -> float:
    return round(size / 1024 / 1024 / 1024, ndigits=2)

def write_csv(samples: dict, out_folder=".", fmt="autofoss_%datetime%.csv") -> str:
    os.makedirs(out_folder, exist_ok=True)
    sample_columns = ['Timestamp', 'Elapsed', 'Current Weight',
                    'Sensor 1', 'Sensor 2', 'Sensor 3', 'Sensor 4',
                    'Sensor 5', 'Sensor 6', 'Sensor 7', 'Sensor 8']
    date_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    file_name = os.path.join(out_folder, fmt.replace('%datetime%', date_time))
    # estimate storage requirement from the first sample
    csv_size = bytes_to_gb(sum([len(str(sample[col])) for col in sample_columns for sample in samples]))
    print(f"Estimated CSV file size: {csv_size} GB")
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