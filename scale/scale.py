import usb.core
import usb.util
import sys
import threading
import pandas as pd
import datetime

debug = True
generateFakeData = True

if not generateFakeData:
    dev = usb.core.find(idVendor=0x1a86,idProduct=0x7523)
    if dev is None:
        raise Exception("Plug in the scale!")
    assert dev is not None
    ep = dev[0].interfaces()[0].endpoints()[0]
    i = dev[0].interfaces()[0].bInterfaceNumber

    dev.reset()


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

charmap = {
    46:  '.',
    48:  '0',
    177: '1',
    178: '2',
    51:  '3',
    180: '4',
    53:  '5',
    54:  '6',
    183: '7',
    184: '8',
    57:  '9',
}

start_seconds = datetime.datetime.now().timestamp()
fake_threshold = None

def decodeThread(r):
    global current_weight
    r = r[:-4]
    decoded = ""
    for i in r:
        if i in charmap:
            decoded += charmap[i]
        else:
            return # invalid data, just wait for a second to get more
    print(decoded, end=" "*30 + "\r")
    try:
        current_weight = float(decoded)
        data.loc[len(data)] = [current_weight, pd.Timestamp.now(), datetime.datetime.now().timestamp() - start_seconds]
    except ValueError:
        print(decoded + " (invalid!)", end="\r")

while True:
    try:
        if not generateFakeData:
            r = dev.read(eaddr, 10)
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