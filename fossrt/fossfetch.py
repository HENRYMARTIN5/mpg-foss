"""
Written by Caleb C. & Andrew Valentini in 2022 for Carthage Space Sciences | WSGC | NASA
Butchered by Henry M. in 2023 for realtime viewing of data.
Collects data from the Gator hardware (or simulator) and saves it to a CSV file.
"""

import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from halo import Halo
from common.formatmodule import bcolors, bsymbols, prints, files
from common.fosmodule import datahelper, gatorpacket, packetsim
import pandas as pd
import time
import usb.core
import usb.util
import array
import struct
import threading
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.animation as anim
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='Fetch data from the Gator hardware and save it to a CSV file.')
parser.add_argument('output', help='The name of the CSV file to save the data to.')
args = parser.parse_args()

csvFile = None

def cog_to_wavelength(binary):
    return 1514+((int(binary, 2) * (1586-1514))/(2 ** 18)) # secret sauce

def parserThread(rxBytes):
    global csvFile
    rxBuffer = array.array('B')
    rxBuffer.extend(rxBytes)
    dataBytes = bytearray(rxBuffer)
    dataBytes.reverse() #May need to reverse or rewrite the datahelper
    #Init console status indicator
    ### Instantiate classes ###
    datum = datahelper()
    simpacket = packetsim()
    pprint = prints()
    #-------------------------#
    #Set print option
    selection_print = False
    printout = False
    selection_csv = False
    save_to_csv = False
    datum.raw_data = dataBytes
    #----------------------------------------------------------------------------------------------#
    ### Next, sort datum for packets ###
    packets = datum.parse()
    #----------------------------------------------------------------------------------------------#
    try:
        # kicked off every time data is recieved so the program can continue working even while data is being parsed
        # prevents issues with sensor data not appearing correctly
        data_frames = []
        for key in packets:
            thispacket = gatorpacket()
            thispacket.raw_data = packets[key]
            #This tuple contains the inner class objects of the packet class.
            pkt_header, pkt_status, pkt_cog = thispacket.create_inner()
            #Pull out relevant values
            pkt_num = pkt_header.get_packet_num()
            pkt_timestamp = pkt_header.get_timestamp()
            #pkt_payload_len = pkt_header.get_payload_len()
            #gator_version = pkt_header.get_version()
            #gator_type = pkt_header.get_gator_type()
            cog_data = pkt_cog.get_cog_data()
            ### Get user decision on handling data ###
            selection_csv = True
            save_to_csv = True
            #TODO: Save to CSV here!
            #------------------------------------------------------------------------------------------------------------------------------------------#
            if save_to_csv is True:
                spinner.start()
                cog = {}
                err = {}
                for key in cog_data.keys():
                    cog[key] = cog_data[key]["cog"]
                    err[key] = cog_data[key]["err"]
                for key, value in cog_data.items():
                    columns = {'packet':pkt_num,'timestamp':pkt_timestamp, 'sensor': key, 'cog': cog[key], 'err': err[key]}
                    data_frames.append(columns)
            #--------------------------------------------------------------------------------------------------------------------#
        print("mpg-foss: Grabbed data frames!")
        # we also want to add this data to the csv file
        for frame in data_frames:
            csvFile.write(f"{frame['packet']},{frame['timestamp']},{frame['sensor']},{frame['cog']},{frame['err']}\n")
    except (KeyError, struct.error):
        print(f"{bcolors.WARNING}mpg-foss: Error parsing data!{bcolors.ENDC}")

# check if the output file exists. if it does, clear it.
with open(args.output, "w") as f:
    f.write("packet,timestamp,sensor,cog,err\n")
csvFile = open(args.output, "a+") # we need to read and append
spinner = Halo(spinner='dots')
errorStatus = False
date = time.strftime("%Y-%m-%d")
f = files()
num_packets = 1
collectDuration = 0

def error_check():
    global errorStatus
    global spinner
    spinner.start()

def detect_gator():
    print(f"{bcolors.ENDC}{bsymbols.info} {bcolors.HEADER}mpg-foss: Searching for gator hardware...{bcolors.ENDC}")
    endpoint = None
    # Find the Gator via vID & pID
    dev = usb.core.find(idVendor=0x0403, idProduct=0x6010)
    # Set endpoint if it was found
    if dev is not None:
        if dev.is_kernel_driver_active(0):
            try:
                dev.detach_kernel_driver(0)
            except usb.core.USBError as e:
                sys.exit("Could not detach kernel driver: ")
        try:
                usb.util.claim_interface(dev, 0)
                print(f"{bcolors.ENDC}{bsymbols.info} {bcolors.HEADER}mpg-foss: Claimed device...{bcolors.ENDC}")
        except:
                endpoint = dev[0][(0,0)][0]
        cfg = dev.get_active_configuration()
        intf = cfg[(0,0)]
        endpoint = usb.util.find_descriptor(
            intf,
            # Match the first IN endpoint
            custom_match = \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                usb.util.ENDPOINT_IN)
        assert endpoint is not None
    return dev, endpoint

def main():
    #Globals
    global errorStatus
    global spinner
    global collectDuration
    global num_packets
    global output_path
    global csvFile

    #Initialize
    spinner.start()
    threads = []

    try:
        gator_tuple = detect_gator()
        dev = gator_tuple[0]
        endpoint = gator_tuple[1]
    except:
        print("Failed to init gator.")
        sys.exit(1)

    starterRxBytes = array.array('B', [0]) * (64 * 8)

    try:
        while True:
            rxBytes = starterRxBytes
            dev.read(endpoint.bEndpointAddress, rxBytes)
            threads.append(threading.Thread(target=parserThread, args=(rxBytes,)))
            threads[-1].start()

    except(KeyboardInterrupt, SystemExit):
        print("mpg-foss: Process aborted.")

    except(struct.error, KeyError):
        print(f"{bcolors.WARNING}mpg-foss: Error parsing data!{bcolors.ENDC}")

    spinner.start()
    total = len(threads)
    i = 0
    for thread in threads:
        spinner.text = f"mpg-foss: Cleaning up threads... {i}/{total}"
        thread.join()
        i += 1
    spinner.succeed("mpg-foss: Threads cleaned up. Exiting...")
    return errorStatus

#Run the main function if this module is called directly.
if __name__ == '__main__':
   main()