from _EbiagiComponent import EbiagiComponent
from _naming_conventions import *
from _Instrument import Instrument
from _Loop import Loop

class Module(EbiagiComponent):

    def __init__(self, track, Set):
        super(Module, self).__init__()
        self._track = track
        self._set = Set
        self.instruments = []
        self.loops = {}

        self.short_name = get_short_name(track.name.split('.')[0])

        self.log('Initializing Module %s...' % self.short_name)

        i = list(self._song.tracks).index(track) + 1
        m = 0
        a = 0
        while not is_module(self._song.tracks[i].name) and self._song.tracks[i].is_grouped:

            #Add Instruments
            if is_instrument(self._song.tracks[i].name):
                instr = Instrument(self._song.tracks[i], Set)
                if instr.has_midi_input():
                    instr.set_midi_router(Set.midi_routers[m])
                    m += 1
                if instr.has_audio_input():
                    instr.set_audio_router(Set.audio_routers[a])
                    a += 1
                self.instruments.append(instr)

            i += 1

        for scene in self._song.scenes:
            if is_loop(scene.name):
                loop = Loop(track, scene, Set, self.instruments)
                self.loops[loop.short_name] = loop

                
    def activate(self):
        self.log('Activating %s...' % self.short_name)
        for instrument in self.instruments:
            instrument.activate()
        self._track.fold_state = 0
        self._track.mute = 0

    def deactivate(self):
        self.log('Deactivating %s...' % self.short_name)
        for instrument in self.instruments:
            instrument.deactivate()
        self._track.fold_state = 1
        self._track.mute = 1