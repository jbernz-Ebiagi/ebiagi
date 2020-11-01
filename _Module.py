from _EbiagiComponent import EbiagiComponent
from _naming_conventions import *
from _Instrument import Instrument

class Module(EbiagiComponent):

    def __init__(self, track, Set):
        super(Module, self).__init__()
        self.track = track
        self.set = Set
        self.instruments = []

        self.short_name = get_short_name(track.name.split('.')[0])

        self.log('Initializing Module %s...' % self.short_name)

        i = list(self._song.tracks).index(track) + 1
        m = 0
        a = 0
        while not is_module(self._song.tracks[i].name) and self._song.tracks[i].is_grouped:

            #Add Instruments
            if is_instrument(self._song.tracks[i].name):
                instr = Instrument(self._song.tracks[i], Set)
                if instr.has_midi_input:
                    instr.set_midi_router(Set.midi_routers[m])
                    m += 1
                if instr.has_audio_input:
                    instr.set_audio_router(Set.audio_routers[a])
                    a += 1
                self.instruments.append(instr)

            i += 1
        
    def activate(self):
        self.log('Activating %s...' % self.short_name)
        for instrument in self.instruments:
            instrument.activate()
        self.track.fold_state = 0
        self.track.mute = 0

    def deactivate(self):
        self.log('Deactivating %s...' % self.short_name)
        for instrument in self.instruments:
            instrument.deactivate()
        self.track.fold_state = 1
        self.track.mute = 1