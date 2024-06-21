from component import AutofossComponent
from msl.equipment import (
    EquipmentRecord,
    ConnectionRecord,
    Backend,
)

class AutofossPowersupply(AutofossComponent):
    def __init__(self, other: dict, address='COM9'):
        self.record = EquipmentRecord(
            manufacturer='Aim-TTi',
            model='MX100TP',
            connection=ConnectionRecord(
                address=address, # can be either an IP address or a COM port
                backend=Backend.MSL,
                timeout=10,
            )
        )
        self.channels = [1, 2, 3]
    
    def start(self):
        self.tti = self.record.connect()

    def stop(self):
        """Turns off all power supply channels. You probably don't want to call this."""
        self.tti.turn_off(1)
        self.tti.turn_off(2)
        self.tti.turn_off(3)
        self.tti.disconnect()
    
    def on(self, channel):
        if type(channel) != int:
            for _channel in channel:
                self.tti.turn_on(_channel)
            return
        self.tti.turn_on(channel)
    
    def off(self, channel):
        if type(channel) != int:
            for _channel in channel:
                self.tti.turn_off(_channel)
            return
        self.tti.turn_off(channel)
    
    def reset(self):
        self.stop()