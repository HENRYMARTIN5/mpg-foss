from component import AutofossComponent, ComponentManager
from msl.equipment import (
    EquipmentRecord,
    ConnectionRecord,
    Backend,
)

class AutofossPowersupply(AutofossComponent):
    def __init__(self, manager: ComponentManager, address='COM9'):
        self.manager = manager # ! unused
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
        self.connected = False
    
    def start(self):
        if not self.connected:
            self.tti = self.record.connect()
            self.connected = True

    def stop(self):
        """Turns off all power supply channels. You probably don't want to call this."""
        self.tti.turn_off(1)
        self.tti.turn_off(2)
        self.tti.turn_off(3)
        self.tti.disconnect()
        self.connected = False
    
    def on(self, channel):
        if not self.connected:
            self.start()
        if type(channel) != int:
            for _channel in channel:
                self.tti.turn_on(_channel)
            return
        self.tti.turn_on(channel)
    
    def off(self, channel):
        if not self.connected:
            self.start()
        if type(channel) != int:
            for _channel in channel:
                self.tti.turn_off(_channel)
            return
        self.tti.turn_off(channel)
    
    def reset(self):
        self.stop()
        
    def pause(self):
        self.powerstate = self.tti.get_output_state()
        self.tti.turn_off(1)
        self.tti.turn_off(2)
        self.tti.turn_off(3)
        
    def resume(self):
        raise NotImplementedError("This method is not implemented for the power supply.")