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

        self.log('create beat selector')

        self._device.view.add_selected_chain_listener(self.on_selected_chain_change)

    def on_selected_chain_change(self):
        if not self._device.is_active:
            return
        self.midi_action(self.activate_devices)

    def activate_devices(self):
        for i, chain in enumerate(self._device.chains):
            if chain == self._device.view.selected_chain:
                for device in chain.devices:
                    device.parameters[0].value = device.parameters[0].max
            else:
                for device in chain.devices:
                    device.parameters[0].value = device.parameters[0].min