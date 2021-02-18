from _EbiagiComponent import EbiagiComponent

class Router(EbiagiComponent):

    def __init__(self, track, Set):
        super(Router, self).__init__()
        self._track = track
        self._set = Set
        self._instrument = None
        self._is_midi = track.has_midi_input

        self._device = track.devices[0]
        self._reset()

    def set_instrument(self, instrument):
        self._instrument = instrument
        self._reset()

    def update_input(self, ipt, iptIdx):
        if self._instrument:
            chain = self._device.chains[iptIdx]
            if ipt.has_instrument(self._instrument):
                chain.mute = 0
            else:
                chain.mute = 1

    def _reset(self):
        for chain in self._device.chains:
            if chain.name == 'THRU':
                chain.mute = 0
            else:
                chain.mute = 1