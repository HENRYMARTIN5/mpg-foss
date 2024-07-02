import serial
from serial.tools import list_ports
import datetime
import re
import string
import threading
import traceback
from component import AutofossComponent, ComponentManager

def remove_all(s, chars):
    for c in chars:
        s = s.replace(c, "")
    return s

def filter_printable(s):
    return ''.join(filter(lambda x: x in string.printable, s))

# HACK: extra charmap to fix the encoding issues with the scale
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

def decode_ascii_with_extra(data: bytes) -> str:
    # HACK: really stupid way to layer the extra encoding... but it works and minimizes the error rate
    dot_point = data.find(b".")
    if dot_point < 3:
        return ""
    for char in extra_charmap:
        data = data.replace(char, extra_charmap[char])
    return data.decode("ascii", errors="ignore")

class AutofossScale(AutofossComponent):
    def __init__(self, manager: ComponentManager, interactive=True, log_scale=False, default_port="COM7", weight_timeout=8, full_weight=18.0):
        print("Available ports:")
        for port in list_ports.comports():
            print("\t" + port.device)
        if not default_port in [port.device for port in list_ports.comports()]:
            if not interactive:
                raise ValueError(f"Default port {default_port} not found. Please specify a port.")
            print(f"Default port {default_port} not found. What port should we use?")
            default_port = input(" -> ")
        print(f"Opening serial port {default_port}...")
        self.ser = serial.Serial(default_port, 9600, timeout=1)
        print("Serial port opened.")
        self.current_weight = 0.0
        self.last_weight_change = datetime.datetime.now().timestamp()
        self.buffer = ""
        self.thread_running = True
        self.thread_initialized = False
        self.log = log_scale
        self.pattern = re.compile(r'\d{1,3}\.\d{2}(?:lb|l)') # compile once, better performance - why wasn't I doing this before??
        self.weight_timeout = weight_timeout
        self.manager = manager
        self.full_weight = full_weight

    def read_scale(self, no_log=False) -> float:
        r = self.ser.read_all()
        decoded = filter_printable(decode_ascii_with_extra(r))
        if decoded.strip() != "":
            self.buffer += decoded
            self.buffer = remove_all(self.buffer, "\r\n")
            matches = self.pattern.findall(self.buffer)
            if len(matches) > 0:
                self.buffer = ""
                weight = float(remove_all(matches[0], "lb"))
                self.thread_initialized = True
                if self.current_weight != weight:
                    self.last_weight_change = datetime.datetime.now().timestamp()
                self.current_weight = weight
                if no_log:
                    return weight
                if self.log:
                    print(f"-> {'{:6.2f}'.format(self.current_weight)}lb - {'{:.2f}'.format(self.current_weight/self.full_weight*100)} % total weight")
                return weight
        return self.current_weight

    def thread(self):
        while self.thread_running:
            gator = self.manager.get('gator')
            if (datetime.datetime.now() - gator.start_time).total_seconds() > 10:
                if not gator.last_packet:
                    print("Gator seems to be disconnected - no packets received in 10 seconds. Stopping...")
                    self.thread_running = False
                    self.thread_initialized = False
                    return
            try:
                if gator.auto_end and datetime.datetime.now().timestamp() - self.last_weight_change > self.weight_timeout:
                    print(f"Tank seems to be drained - no weight changes in {datetime.datetime.now().timestamp() - self.last_weight_change} seconds, over threshold of {self.weight_timeout} seconds. Stopping...")
                    self.thread_running = False
                    self.thread_initialized = False
                    return
                self.read_scale()
            except Exception as e:
                print("Error in scale thread:", e)
                traceback.print_exc()
    
    def start(self):
        self.thread_initialized = False
        self.thread_running = True
        self.t = threading.Thread(target=self.thread)
        self.t.start()
    
    def stop(self):
        self.thread_running = False
        self.t.join()

    def reset(self):
        self.thread_initialized = False
        self.thread_running = False
        self.buffer = ""
        self.current_weight = 0.0
        self.last_weight_change = datetime.datetime.now().timestamp()
    
    def wait_for_thread(self):
        # returns bool, bool - graceful stop, force stop
        # wait for the thread to finish - if the user interrupts once, wait for the thread to finish and return the values for a graceful stop
        # if the user interrupts a second time... return the values for a force stop
        try:
            print("Press CTRL+C to stop.")
            while self.thread_running:
                pass
            return False, False
        except KeyboardInterrupt:
            try:
                print("Interrupted. Shutting down gracefully - press CTRL+C again to force shutdown.")
                while self.thread_running:
                    pass
                return True, False
            except KeyboardInterrupt:
                print("Forcing shutdown.")
                return True, True
            
    def pause(self):
        raise NotImplementedError("whoops")
    
    def resume(self):
        raise NotImplementedError("whoops")