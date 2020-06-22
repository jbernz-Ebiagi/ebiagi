from _Instrument import Instrument
from _utils import catch_exception, is_module, is_instrument

class Module:

    @catch_exception
    def __init__(self, track, Set):
        self.set = Set
        
        self.track = track
        self.instruments = []
        self.held_instruments = set([])
        self.module_fx = []

        i = self.set.tracks.index(track) + 1
        while not is_module(self.set.tracks[i]) and self.set.tracks[i].is_grouped:
            if is_instrument(self.set.tracks[i]):
                instrument = Instrument(self.set.tracks[i], self)
                self.instruments.append(instrument)
            i += 1

    def select_instrument(self, index):
        self.held_instruments.add(self.instruments[index])
        self.arm_instruments()

    def deselect_instrument(self, index):
        self.held_instruments.remove(self.instruments[index])
        if len(self.held_instruments) > 0:
            self.arm_instruments()

    def arm_instruments(self):
        for instrument in self.instruments:
            if instrument in self.held_instruments:
                instrument.arm(self.set.held_inputs)
            else:
                instrument.disarm(self.set.held_inputs)

    def activate(self):
        self.log('activate ' + self.track.name)
        for instrument in self.instruments:
            instrument.activate()
        self.track.fold_state = 0

    def deactivate(self):
        self.log('deactivate ' + self.track.name)
        for instrument in self.instruments:
            instrument.deactivate()
        self.track.fold_state = 1

    def log(self, msg):
        self.set.log(msg)