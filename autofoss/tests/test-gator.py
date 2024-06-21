# -*- coding: utf-8 -*-
# Copyright (C) PhotonFirst Technologies B.V. See LICENSE for details.
"""
Sample application demonstrating how to use the PhotonFirst Gator Python API

Prior to running this script please make sure the PhotonFirst Gator Python API
has been installed and the Gator(s) are connected to the system.

The PhotonFirst Gator API can be installed using the following command:
`pip install gator_api-x.x.x-py3-none-any.whl`
"""
import csv
import datetime
import sys
import logging
from logging.handlers import RotatingFileHandler

from gator_api.gator_api import GatorApi
from gator_api.gator_data import GatorData

def create_logger():
    """ Creates a default logger for writing diagnostics information to file

    @return Logger
    """
    logger = logging.getLogger(__name__)
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s:%(lineno)d %(message)s')
    handler = RotatingFileHandler('photonfirst-api.log',
                                  maxBytes=(5 * 1024 * 1024),  # 5 MB
                                  backupCount=1)               # 2 logfiles (rotated)
    handler.setFormatter(log_formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger


def do_get_ffactor(api, gator):
    """ Demonstrates how to get the F-Factor value from the Gator

    @param gator Reference to the Gator object
    @return None
    """
    print('Reading the F-Factor...')
    ffactor = api.get_ffactor(gator)
    print(f'F-Factor value = {ffactor}')


def do_set_ffactor(api, gator):
    """ Demonstrates how to set the F-Factor

    @param gator Reference to the Gator object
    @return None
    """
    print('Please enter new F-Factor value [integer between 8-127]: ')
    ffactor = int(input())

    print(f'Setting the F-Factor to {ffactor}...')
    api.set_ffactor(gator, ffactor)
    print('F-factor set!')


def do_get_samplefrequency(api, gator):
    """ Demonstrates how to get the sample frequency value from the Gator

    @param gator Reference to the Gator object
    @return None
    """
    print('Reading the sample frequency...')
    samplefrequency = api.get_samplefrequency(gator)
    print(f'Sample frequency = {samplefrequency} kHz')


def do_set_samplefrequency(api, gator):
    """ Demonstrates how to set the sample frequency

    @param gator Reference to the Gator object
    @return None
    """
    print('Please enter new samplefrequency index [1 = 1kHz, 2 = 5kHz, 3 = 10kHz, 4 = 19kHz]: ')
    samplefrequency = int(input())

    print(f'Setting the sample frequency to {samplefrequency}...')
    api.set_samplefrequency(gator, samplefrequency)
    print('Sample frequency set!')


def do_get_threshold(api, gator):
    """ Demonstrates how to get the CoG threshold from the Gator

    @param gator Reference to the Gator object
    @return None
    """
    print('Reading the CoG threshold...')
    cog_threshold = api.get_cogthreshold(gator)
    print(f'CoG threshold value = {cog_threshold}')


def do_set_threshold(api, gator):
    """ Demonstrates how to set the CoG threshold

    @param gator Reference to the Gator object
    @return None
    """
    print('Please enter new CoG value [integer]: ')
    cog_value = int(input())

    print(f'Setting the CoG threshold to {cog_value}...')
    api.set_cogthreshold(gator, cog_value)
    print('CoG threshold set!')

def do_get_raw_adas_values(api, gator):
    """ Demonstrates how to get the RAW ADAS values from the Gator

    @param gator Reference to the Gator object
    @return None
    """
    print('Reading the RAW ADAS values...')
    adas_values = api.get_raw_adas_values(gator)
    print(f'Raw ADAS values ({len(adas_values)}) = {adas_values}')


def do_set_averaging(api, gator):
    """ Enable averaging of output data between switches

    @param gator Reference to the Gator object
    @return None
    """
    yes_choices = ['yes', 'y']

    print('Enable averaging [Y/N]: ')
    user_input = input()

    if user_input.lower() in yes_choices:
        print('Enabling averaging ...')
        api.enable_average(gator, True)
        print('Averaging enabled.')
    else:
        print('Disabling averaging ...')
        api.enable_average(gator, False)
        print('Averaging disabled.')

def do_set_switch_channel_range(api, gator):
    """ Sets the channel switch range

    @param gator Reference to the Gator object
    @return None
    """
    print('Please enter the start channel [1 - 8]: ')
    start_channel = int(input())
    print('Please enter the end channel [1 - 8]: ')
    end_channel = int(input())

    print(f'Setting channel switch range from {start_channel} to {end_channel} ...')
    api.set_channel_range(gator, start_channel, end_channel)
    print('Switching configured!')

def do_set_switch_time(api, gator):
    """ Sets the channel switch time

    @param gator Reference to the Gator object
    @return None
    """
    print('Please enter the channel [1 - 8] (0 = All): ')
    channel = int(input())
    print('Please enter the switch time [2500 - 16777215]: ')
    switch_time = int(input())

    if channel > 0:
        print(f'Setting channel switch time for channel {channel} to {switch_time} ...')
        api.set_switch_time(gator, channel, switch_time)
        print('Switch time configured!')
    else:
        for channel in range (1, 9):
            print(f'Setting channel switch time for channel {channel} to {switch_time} ...')
            api.set_switch_time(gator, channel, switch_time)
            print('Switch time configured!')

def do_streaming_to_csv(api, logger, gator):
    """ Demonstrates how to stream measurement samples from the Gator to a CSV file

    @param gator Reference to the Gator object
    @return None
    """
    samples = []

    def on_sample_received(data_array):
        """ Callback function. This method is called
        when a new sample has been received

        @param data_array An array of samples (sample is a dictionary based on sample_columns)
        """
        for sample in data_array:
            print(sample)
            samples.append(sample)

    print('Streaming data to CSV file...')

    gator_data = GatorData(api, logger)
    gator_data.register_callback(on_sample_received)
    api.start_streaming(gator)
    gator_data.start_streaming()

    input('Press ENTER to stop streaming.')
    print('Streaming stopped. Processing remaining samples...')

    api.stop_streaming(gator)
    gator_data.stop_streaming()

    print('Processing finished.')

    print('Writing samples to CSV...')
    sample_columns = ['GOS timestamp', 'GTR timestamp', 'Packet counter', 'Gator index',
                      'Sync status', 'TEC status', 'Channel', 'Sensors',
                      'Sensor 1', 'Sensor 2', 'Sensor 3', 'Sensor 4',
                      'Sensor 5', 'Sensor 6', 'Sensor 7', 'Sensor 8']

    date_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    file_name = f'{date_time}_gator_data.csv'

    with open(file=file_name, mode='w', encoding='utf-8', newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, sample_columns)
        csv_writer.writeheader()

        for sample in samples:
            csv_writer.writerow(sample)



def main():
    """ Application main entry point
    """
    try:
        print('PhotonFirst Gator API library - Sample application')
        logger = create_logger()

        # Initialize the api by instantiating the GatorApi class.
        api = GatorApi(logger)

        # Set log level to WARNING, instead of the standard INFO
        api.set_gator_log_level(4)

        # Query for connected gators
        gators = api.query_gators()

        nr_of_gators = len(gators)
        plural_postfix = "" if nr_of_gators == 1 else "s"
        print(f'Found {nr_of_gators} gator{plural_postfix} on the system')

        if nr_of_gators < 1:
            print('No gators found, ending application.')
            return

        # Connect to the first gator
        api.connect(gators[0])

        print('Please note that this sample application will communicate with the first gator only.')

        # Create a simple menu allowing the user to select various options
        choice = 'x'
        while choice != '0':
            print('')
            print("Please select one of the following options: ")
            print('')
            print('[1] Get F-Factor')
            print('[2] Set F-Factor')
            print('[3] Get sample frequency')
            print('[4] Set sample frequency')
            print('[5] Get CoG threshold')
            print('[6] Set CoG threshold')
            print('[7] Get raw ADAS values')
            print('[8] Set switch channel range')
            print('[9] Set switch time')
            print('[10] Enable/disable averaging')
            print('[11] Stream data to CSV file')
            print('[12] Stream shape data to CSV file')
            print('')
            print('[0] EXIT')
            choice = input('Please type the number of the option and press ENTER: ')

            if choice == '1':
                do_get_ffactor(api, gators[0])
            elif choice == '2':
                do_set_ffactor(api, gators[0])
            elif choice == '3':
                do_get_samplefrequency(api, gators[0])
            elif choice == '4':
                do_set_samplefrequency(api, gators[0])
            elif choice == '5':
                do_get_threshold(api, gators[0])
            elif choice == '6':
                do_set_threshold(api, gators[0])
            elif choice == '7':
                do_get_raw_adas_values(api, gators[0])
            elif choice == '8':
                do_set_switch_channel_range(api, gators[0])
            elif choice == '9':
                do_set_switch_time(api, gators[0])
            elif choice == '10':
                do_set_averaging(api, gators[0])
            elif choice == '11':
                do_streaming_to_csv(api, logger, gators[0])
            elif choice == '0':
                print('Closing application.')
            else:
                print('Invalid choice.')

    # The api object will raise an exception in case of failure.
    # Additional information on the error can be extracted from
    except KeyboardInterrupt:
        print('User terminated the application')
    except EOFError:
        print('User terminated the application')
    except RuntimeError as unexpected_error:
        print(f'An unexpected exception occured: {unexpected_error}')

if __name__ == '__main__':
    sys.exit(main())
