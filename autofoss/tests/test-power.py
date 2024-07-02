from power import AutofossPowersupply, ComponentManager
import time

def test_autofoss_powersupply():
    power = AutofossPowersupply(ComponentManager(), address='COM9')
    power.start()
    power.on(3)
    time.sleep(0.5)
    power.off(3)