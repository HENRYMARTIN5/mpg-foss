import serial
from serial.tools import list_ports
import string
import re

DEFAULT_PORT = "COM7"
print("Available ports:")
for port in list_ports.comports():
    print("\t" + port.device)
if not DEFAULT_PORT in [port.device for port in list_ports.comports()]:
    print(f"Default port {DEFAULT_PORT} not found. What port should we use?")
    DEFAULT_PORT = input(" -> ")
print(f"Opening serial port {DEFAULT_PORT}...")
ser = serial.Serial(DEFAULT_PORT, 9600, timeout=1)
print("Serial port opened.")

def encode_cmd(cmd):
    return (cmd + "\r").encode("ascii")

def filter_printable(s):
    return ''.join(filter(lambda x: x in string.printable, s))

def remove_all(s, chars):
    for c in chars:
        s = s.replace(c, "")
    return s

commands = {
    "weight": encode_cmd("W"),
    "status": encode_cmd("S"),
    "zero":   encode_cmd("Z")
}

current_weight = 0.0
buffer = ""
pattern = re.compile(r'\d{1,3}\.\d{2}(?:lb|l)') # compile once, better performance - why wasn't I doing this before??
while True:
    r = ser.read_all()
    decoded = filter_printable(r.decode("ascii", errors="ignore"))
    if decoded.strip() != "":
        buffer += decoded
        buffer = remove_all(buffer, "\r\n")
        matches = pattern.findall(buffer)
        if len(matches) > 0:
            buffer = ""
            weight = float(remove_all(matches[0], "lb"))
            print(f"{weight}lb" + (" " * 15), end="\r")
        else:
            # print("No match" + (" " * 15), end="\r")
            pass

ser.close()