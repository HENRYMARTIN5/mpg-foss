import pandas as pd
import os
import time
import usb.core
import usb.util
import sys
import array
from fosmodule import datahelper, gatorpacket, packetsim
from formatmodule import prints
import struct
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import threading
import mplcursors
from cog import cog_to_wavelength

def detect_gator():
    print("Searching for Gator...")
    endpoint = None
    time.sleep(0.65)
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
                print(f"Claimed device...")
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
    dev, endpoint = detect_gator()
    if dev == None:
        print("Failed to find Gator.")
        sys.exit(1)
    print(str(endpoint))
    print("Beginning realtime collection...")

    packets = []
    fullFrames = []

    for i in range(1,3):
        rxBytes = array.array('B', [0]) * (64 * 8)
        rxBuffer = array.array('B')
        collectDuration = 1
        #Run a loop for the specified duration in seconds:
        start_time = time.time()
        while time.time() - start_time < collectDuration:
            dev.read(endpoint.bEndpointAddress, rxBytes)
            rxBuffer.extend(rxBytes)
        dataBytes = bytearray(rxBuffer)
        dataBytes.reverse() #May need to reverse or rewrite the datahelper
        datum = datahelper()
        datum.raw_data = dataBytes
        packetchunk = datum.parse()
        packets.append(packetchunk)
        frames = []
        for key in packetchunk:
            frame = []
            thispacket = gatorpacket()
            thispacket.raw_data = packetchunk[key]
            pkt_header, pkt_status, pkt_cog = thispacket.create_inner()
            pkt_num = pkt_header.get_packet_num()
            pkt_timestamp = pkt_header.get_timestamp()
            cog_data = pkt_cog.get_cog_data()
            cog = {}
            err = {}
            for key, value in cog_data.items():
                for k, v in value.items():
                    if k == "cog":
                        cog[key] = v
                    elif k == "err":
                        err[key] = v
            for key, value in cog_data.items():
                columns = {'packet':pkt_num,'timestamp':pkt_timestamp, 'sensor': key, 'cog': cog[key], 'err': err[key]}
                frame.append(columns)
            frames.append(frame)
        # print(frames)
        fullFrames.append(frames)
        # TODO: realtime plot
    # assemble data
    sensorFrames = []
    mergeme = []
    for frames in fullFrames:
        for _frame in frames:
            for frame in _frame:
                sensorVals = {
                    "1": [],
                    "2": [],
                    "3": [],
                    "4": [],
                    "5": [],
                    "6": [],
                    "7": [],
                    "8": []
                }
                sensorNum = str(int(frame['sensor'].split("_")[1])) # convert back and forth to remove prefixed 0
                sensorVals[sensorNum].append(cog_to_wavelength(frame['cog']))
                sensorFrames.append(sensorVals)
            #print(sensorVals)
            mergeme.append(sensorVals)
    #print(sensorFrames)
    sensorVals = {
        "1": [],
        "2": [],
        "3": [],
        "4": [],
        "5": [],
        "6": [],
        "7": [],
        "8": []
    }
    for value in mergeme:
        for k, v in value.items():
            for read in v:
                sensorVals[k].append(read)
    

    





    dev.reset()
    print("Done. Data should have printed.")

if __name__ == "__main__":
    try:
        main()
    except struct.error:
        print("Error getting data from Gator.")
    except KeyboardInterrupt:
        print("Interrupted.")
