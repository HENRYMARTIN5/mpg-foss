from power import AutofossPowersupply
import time

def test_autofoss_powersupply():
    components = {}
    components['power'] = AutofossPowersupply(components, address='COM9')
    power = components['power']
    power.start()
    power.on(3)
    time.sleep(500)
    power.off(3)