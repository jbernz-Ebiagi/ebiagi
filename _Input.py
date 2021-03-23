from ._EbiagiComponent import EbiagiComponent
from ._naming_conventions import *

class Input(EbiagiComponent):

    def __init__(self, track, Set):
        super(Input, self).__init__()
        self._track = track
        self._set = Set
        self._instruments = set([])

        self.has_audio_input = track.has_audio_input
        self.has_midi_input = track.has_midi_input

        self.short_name = get_short_name(track.name)

        self.phantom_instrument = None

        self.log('Initializing Input %s...' % self.short_name)

    def add_instrument(self, instrument):
        self._instruments.add(instrument)
        self.phantom_instrument = None

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