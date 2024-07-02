from component import AutofossComponent, ComponentManager
import threading
import datetime
import time

class AutofossRefiller(AutofossComponent):
    def __init__(self, manager: ComponentManager, threshold=3.65, extra=5.0):
        self.power = manager.get('power')
        self.scale = manager.get('scale')
        self.threshold = threshold
        self.refilled = False
        self.refill_progress = 0  # % full
        self.extra = extra

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
        weight = self.scale.read_scale(no_log=True)
        if weight < self.threshold:
            return  # no need to refill, tank is already full
        self.power.on(2)
        i = 0
        while not refilled:
            i += 1
            weight = self.scale.read_scale(no_log=True)
            if weight < self.threshold:
                time.sleep(self.extra)  # Keep the pump on for extra seconds
                refilled = True
                self.power.off(2)
                break
            if i % 100 == 0:
                print(f"Refilling tank... currently at {weight}lbs")
        print("Tank refilled.")

    def refill_thread(self):
        weight = self.scale.read_scale(no_log=True)
        start_weight = weight
        if weight < self.threshold:
            self.refilled = True
            return  # no need to refill, tank is already full
        self.power.on(2)
        i = 0
        while not self.refilled:
            i += 1
            weight = self.scale.read_scale(no_log=True)
            try:
                self.refill_progress = (weight - start_weight) / (self.threshold - start_weight) * 100
            except ZeroDivisionError:
                self.refill_progress = -1
            if weight < self.threshold:
                time.sleep(self.extra)  # Keep the pump on for extra seconds
                self.refilled = True
                self.power.off(2)
                break
            if i % 100 == 0:
                print(f"Refilling tank... currently at {weight}lbs, {'{0:.2f}'.format(self.refill_progress)}% full")
        print("Tank refilled.")
        
    def pause(self):
        pass
    
    def resume(self):
        pass