"""
Script for reading from the SBI-240 via the RS-232 serial port.

Make sure the scale is at factory defaults, except for:
User -> COM1 -> Mode -> Continuous
"""

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

extra_charmap = {
    b"\xa0": b"\x20", # space
    b"\xb0": b"\x30", # 0
    b"\xb1": b"\x31", # 1
    b"\xb2": b"\x32", # 2
    b"\xb3": b"\x33", # 3
    b"\xb4": b"\x34", # 4
    b"\xb5": b"\x35", # 5
    b"\xb6": b"\x36", # 6
    b"\xb7": b"\x37", # 7
    b"\xb8": b"\x38", # 8
    b"\xb9": b"\x39", # 9
}
current_weight = 0.0
buffer = ""
pattern = re.compile(r'\d{1,3}\.\d{2}(?:lb|l)') # compile once, better performance - why wasn't I doing this before??

def decode_ascii_with_extra(data: bytes) -> str:
    # HACK: really stupid way to layer the extra encoding... but it works and minimizes the error rate
    dot_point = data.find(b".")
    if dot_point < 3:
        return ""
    for char in extra_charmap:
        data = data.replace(char, extra_charmap[char])
    return data.decode("ascii", errors="ignore")

while True:
    r = ser.read_all()
    decoded = filter_printable(decode_ascii_with_extra(r))
    if decoded.strip() != "":
        buffer += decoded
        buffer = remove_all(buffer, "\r\n")
        matches = pattern.findall(buffer)
        if len(matches) > 0:
            buffer = ""
            weight = float(remove_all(matches[0], "lb"))
            print(f"-> {'{:6.2f}'.format(weight)}lb" + (" " * 15), end="\r")
        else:
            # print("No match" + (" " * 15), end="\r")
            pass

ser.close()