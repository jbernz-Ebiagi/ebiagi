from ._EbiagiComponent import EbiagiComponent
from ._naming_conventions import *

class Input(EbiagiComponent):

    def __init__(self, track, Set, update=None):
        super(Input, self).__init__()
        self._track = track
        self._set = Set
        self._instruments = set([])

        self.has_audio_input = track.has_audio_input
        self.has_midi_input = track.has_midi_input

        self.short_name = get_short_name(track.name)

        self.phantom_instrument = None

        self.update_device = update

        self.log('Initializing Input %s...' % self.short_name)

    def add_instrument(self, instrument):
        self._instruments.add(instrument)
        self.phantom_instrument = None

        #if selecting a new instrument, send feedback to input hardware
        self.log('add instrument')
        self.log(self._instruments)
        self.log(self.update_device)
        if(len(self._instruments) == 1 and self.update_device):
            self.log('update device')
            self.update_device(instrument._track)

    def remove_instrument(self, instrument):
        if instrument in self._instruments:
            self._instruments.remove(instrument)

            if self.empty():
                self.phantom_instrument = instrument

    def has_instrument(self, instrument):
        return instrument in self._instruments or instrument == self.phantom_instrument

    def toggle(self):
        self._track.mute = not self._track.mute

    def is_active(self):
        return not self._track.mute

    def empty(self):
        return len(self._instruments) == 0

    def clear(self):
        self._instruments = set([])
        self.phantom_instrument = None