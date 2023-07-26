import usb.core
import usb.util
import sys
import threading
import pandas as pd

dev = usb.core.find(idVendor=0x1a86,idProduct=0x7523)
if dev is None:
    raise Exception("Plug in the scale!")
assert dev is not None
ep = dev[0].interfaces()[0].endpoints()[0]
i = dev[0].interfaces()[0].bInterfaceNumber

dev.reset()

debug = True

if dev.is_kernel_driver_active(i):
    try:
        dev.detach_kernel_driver(i)
    except usb.core.USBError as e:
        raise Exception("Failed to detatch kernel driver: %s" % str(e))
    
data = pd.DataFrame(columns=["weight", "time"])
    
dev.set_configuration()

eaddr = ep.bEndpointAddress

curent_weight = 0.0

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
        data.loc[len(data)] = [current_weight, pd.Timestamp.now()]
    except ValueError:
        print(decoded + " (invalid!)", end="\r")

while True:
    try:
        r = dev.read(eaddr, 10)
        t = threading.Thread(target=decodeThread, args=(r,))
        t.start()
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