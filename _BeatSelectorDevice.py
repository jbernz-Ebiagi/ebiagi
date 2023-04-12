from functools import partial
import math
from ._EbiagiComponent import EbiagiComponent
from ._naming_conventions import *
import Live

class BeatSelectorDevice(EbiagiComponent):

    def __init__(self, device, instrument):
        super(BeatSelectorDevice, self).__init__()
        self._device = device
        self._instrument = instrument

        self.beats = self.get_beats()

        self.select_knob = self.get_select_knob()   
        self.select_knob.add_value_listener(self.on_select_knob_change)


    def on_select_knob_change(self):
        if not self._device.is_active:
            return
        self.midi_action(self.activate_devices)

    def activate_devices(self):
        selected_beat = self.get_selected_beat()
        for i, chain in enumerate(self._device.chains):
            if chain.name == selected_beat:
                for device in chain.devices:
                    device.parameters[0].value = device.parameters[0].max
            else:
                for device in chain.devices:
                    device.parameters[0].value = device.parameters[0].min

    def get_select_knob(self):
        for param in self._device.parameters:
            if param.name == 'BEAT SELECT':
                return param

    def get_beats(self):
        beats = []
        for param in self._device.parameters:
            if param.name != 'Device On' and param.name != 'BEAT SELECT' and param.name != 'CLIP SELECT' and not param.name.startswith('Macro'):
                beats.append(param)
        return beats

    def get_selected_beat(self):
        beats = self.beats       
        current_beat = beats[0]
        selected_value = self.select_knob.value
        for b in self.beats:
            if b.value <= selected_value and b.value > current_beat.value:
                current_beat = b
        return current_beat.name

    def disconnect(self):
        super(BeatSelectorDevice, self).disconnect()
        if(self.select_knob.value_has_listener(self.on_select_knob_change)):
            self.select_knob.remove_value_listener(self.on_select_knob_change)