from gator_api.gator_api import GatorApi
from gator_api.gator_data import GatorData
import logging
from logging.handlers import RotatingFileHandler
import datetime
from common import AutofossComponent

def to_nm(sample):
    return sample/100000 # HACK: terrible conversion method but it works

def convert_sample(sample):
    global current_weight
    return {
        "GOS timestamp": sample["GOS timestamp"],
        "GTR timestamp": sample["GTR timestamp"],
        "Current Weight": current_weight,
        "Sensor 1": to_nm(sample["Sensor 1"]),
        "Sensor 2": to_nm(sample["Sensor 2"]),
        "Sensor 3": to_nm(sample["Sensor 3"]),
        "Sensor 4": to_nm(sample["Sensor 4"]),
        "Sensor 5": to_nm(sample["Sensor 5"]),
        "Sensor 6": to_nm(sample["Sensor 6"]),
        "Sensor 7": to_nm(sample["Sensor 7"]),
        "Sensor 8": to_nm(sample["Sensor 8"])
    }

class AutofossGator(AutofossComponent):
    def __init__(self, other: dict, auto_end=True, log_gator=False):
        self.logger = logging.getLogger(__name__)
        log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s:%(lineno)d %(message)s')
        handler = RotatingFileHandler('photonfirst-api.log',
                                        maxBytes=(5 * 1024 * 1024),  # 5 MB
                                        backupCount=1)               # 2 logfiles (rotated)
        handler.setFormatter(log_formatter)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(handler)
        self.api = GatorApi(self.logger)
        self.api.set_gator_log_level(4)
        gators = self.api.query_gators()
        nr_of_gators = len(gators)
        plural_postfix = "" if nr_of_gators == 1 else "s"
        print(f'Found {nr_of_gators} gator{plural_postfix} on the system')
        if nr_of_gators < 1:
            raise Exception("Plug in the Gator and **TURN IT ON** before running this script.")
        self.gator = gators[0]
        self.api.connect(self.gator)
        self.scale = other['scale']
        self.power = other['power']
        self.auto_end = auto_end
        self.log = log_gator
        self.samples = []

    def on_sample_received(self, data_array):
        for sample in data_array:
            if not self.scale.thread_initialized:
                continue
            if self.auto_end and datetime.datetime.now().timestamp() - self.scale.last_weight_change > self.scale.weight_timeout:
                print(f"Tank seems to be drained - no weight changes in {datetime.datetime.now().timestamp() - self.scale.last_weight_change} seconds, over threshold of {self.scale.weight_timeout} seconds. Stopping...")
                self.scale.thread_running = False
                return
            if self.log:
                print(sample) # kills performance, but useful for debugging
            self.samples.append(convert_sample(sample))

    def start(self):
        print("Enabling static...")
        self.power.on(1)
        self.gator_data = GatorData(self.api, self.logger)
        self.gator_data.register_callback(self.on_sample_received)
        self.api.start_streaming(self.gator)
        self.power.on(3)
        self.gator_data.start_streaming()
    
    def stop(self):
        self.power.off([1, 3])
        self.api.stop_streaming(self.gator)
        self.gator_data.stop_streaming()
    
    def reset(self):
        self.samples = []
