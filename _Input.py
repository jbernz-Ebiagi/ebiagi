from ._EbiagiComponent import EbiagiComponent
from ._naming_conventions import *

class Input(EbiagiComponent):

    def __init__(self, track, Set, update=None):
        super(Input, self).__init__()
        self._track = track
        self._set = Set
        self._instruments = set([])

        self.selected_instrument = None

        self.has_audio_input = track.has_audio_input
        self.has_midi_input = track.has_midi_input

        self.short_name = get_short_name(track.name)

        self.update_device = update

        self.log('Initializing Input %s...' % self.short_name)

    def add_instrument(self, instrument):
        self._instruments.add(instrument)
        if len(self._instruments) == 1:
            self.set_instrument(instrument)
        else:
            for instrument in self._instruments:
                instrument.disarm()

    def reset_instruments(self, instrument):
        self._instruments = set([])
    
    def set_instrument(self, instrument):
        for instrument in self._instruments:
            instrument.disarm()
        self.selected_instrument = instrument
        self.selected_instrument.arm()
        #if selecting a new instrument, send feedback to input hardware
        if self.update_device:
            self.update_device(instrument._track)

    def has_instrument(self, instrument):
        return self.selected_instrument is instrument

    def toggle(self):
        self._track.mute = not self._track.mute

    def is_active(self):
        return not self._track.mute

    def empty(self):
        return len(self._instruments) == 0

    def clear(self):
        self._instruments = set([])
        if self.selected_instrument:
            self.selected_instrument.disarm()
        self.phantom_instrument = None