from common import AutofossComponent
import threading
import datetime

class AutofossRefiller(AutofossComponent):
    def __init__(self, other: dict, threshold=3.65):
        self.power = other['power']
        self.scale = other['scale']
        self.threshold = threshold
        self.refilled = False
        self.refill_progress = 0 # % full

    def start(self):
        self.t = threading.Thread(target=self.refill_thread)
        self.t.start()
    
    def wait_for_refill(self, timeout_secs=None) -> bool:
        if timeout_secs:
            start_time = datetime.datetime.now().timestamp()
        try:
            while not self.refilled:
                if timeout_secs and datetime.datetime.now().timestamp() - start_time > timeout_secs:
                    return False
        except KeyboardInterrupt:
            print("Refill interrupted! Halting immediately.")
            return False
        return True
    
    def stop(self):
        self.refilled = True
        self.t.join()
    
    def reset(self):
        self.refilled = False

    def refill(self):
        refilled = False
        weight = self.scale.read_scale()
        if weight < self.threshold:
            return # no need to refill, tank is already full
        self.power.on(2)
        i = 0
        while not refilled:
            i += 1
            weight = self.scale.read_scale()
            if weight < self.threshold:
                refilled = True
                self.power.off(2)
                break
            if i % 100 == 0:
                print(f"Refilling tank... currently at {weight}lbs", end='\r')
        print("Tank refilled.")
    
    def refill_thread(self):
        # slightly different implementation to allow for threading and reading the current state from outside the class
        weight = self.scale.read_scale()
        start_weight = weight
        if weight < self.threshold:
            self.refilled = True
            return # no need to refill, tank is already full
        self.power.on(2)
        i = 0
        while not self.refilled:
            i += 1
            weight = self.scale.read_scale()
            self.refill_progress = (weight - start_weight) / (self.threshold - start_weight) * 100
            if weight < self.threshold:
                self.refilled = True
                self.power.off(2)
                break
            if i % 100 == 0:
                print(f"Refilling tank... currently at {weight}lbs, {self.refill_progress}% full", end='\r')
        print("Tank refilled.")