import usb.core
import usb.util
import sys
import threading
import pandas as pd
import datetime
import sys
import traceback
import re

debug = True
generateFakeData = False

if not generateFakeData:
    dev = usb.core.find(idVendor=0x1a86, idProduct=0x7523)
    if dev is None:
        raise Exception("Plug in the scale!")
    assert dev is not None
    ep = dev[0].interfaces()[0].endpoints()[0]
    i = dev[0].interfaces()[0].bInterfaceNumber

    dev.reset()

    if not sys.platform.startswith('win'):
        if dev.is_kernel_driver_active(i):
            try:
                dev.detach_kernel_driver(i)
            except usb.core.USBError as e:
                raise Exception("Failed to detatch kernel driver: %s" % str(e))
    
data = pd.DataFrame(columns=["weight", "time", "matlab_time"])
    
if not generateFakeData:
    dev.set_configuration()
    eaddr = ep.bEndpointAddress

current_weight = 0.0

start_seconds = datetime.datetime.now().timestamp()
fake_threshold = None

def decodeThread(r):
    global current_weight
    if len(r) < 11 or len(r) > 13:
        return
    r = bytearray(r)
    print(r)
    r = r.decode("ascii", errors="ignore").replace(" ", "space").replace("\n", "newline").replace("\r", "return")
    print(r)
    pattern = re.compile(r'\b\d{1,3}\.\d{2}(?:lb|l)\b')
    matches = pattern.findall(r)
    if len(matches) == 0:
        return
    weight = matches[0].replace('l', '').replace('b', '')
    try:
        current_weight = float(weight)
        print("Weight: %slb" % current_weight)
        data.loc[len(data)] = [current_weight, pd.Timestamp.now(), datetime.datetime.now().timestamp() - start_seconds]
    except ValueError:
        traceback.print_exc()

while True:
    try:
        if not generateFakeData:
            r = dev.read(eaddr, 128, timeout=1000)
            t = threading.Thread(target=decodeThread, args=(r,))
            t.start()
        else:
            if not (datetime.datetime.now().timestamp() - start_seconds > 30 or current_weight > 14.75):
                current_weight += 0.1
                fake_threshold = datetime.datetime.now().timestamp() - start_seconds + 1
            else:
                if datetime.datetime.now().timestamp() - start_seconds > fake_threshold:
                    raise KeyboardInterrupt
            data.loc[len(data)] = [round(current_weight, 2), pd.Timestamp.now(), datetime.datetime.now().timestamp() - start_seconds]
    except usb.core.USBTimeoutError:
        if debug:
            print("timeout\n")
    except usb.core.USBError:
        if debug:
            print("usberror\n")
    except KeyboardInterrupt:
        print(" "*30 + "\nSaving csv and exiting...")
        data.to_csv("weight_data.csv", index=False)
        sys.exit(0)
    except Exception as e:
        raise Exception("Something went wrong: %s" % str(e))