from _EbiagiComponent import EbiagiComponent

class Router(EbiagiComponent):

    def __init__(self, track, Set):
        super(Router, self).__init__()
        self._track = track
        self._set = Set
        self._instrument = None

        self._device = track.devices[0]
        for chain in self._device.chains:
            chain.mute = 1

    def set_instrument(self, instrument):
        self._instrument = instrument
        for chain in self._device.chains:
            chain.mute = 1

    def update_input(self, ipt):
        self.log('update router')
        self.log(self._instrument)
        if self._instrument:
            for chain in self._device.chains:
                if chain.name == ipt.short_name:
                    if ipt.has_instrument(self._instrument):
                        chain.mute = 0
                    else:
                        chain.mute = 1