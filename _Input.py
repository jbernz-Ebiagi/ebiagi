from _Framework.ControlSurface import get_control_surfaces
from ._EbiagiComponent import EbiagiComponent
from ._naming_conventions import *

class Input(EbiagiComponent):

    def __init__(self, track, Set):
        super(Input, self).__init__()
        self._track = track
        self._set = Set
        self._instruments = set([])

        self.selected_instrument = None

        self.has_audio_input = track.has_audio_input
        self.has_midi_input = track.has_midi_input

        self.short_name = get_short_name(track.name)

        self.log('Initializing Input %s...' % self.short_name)

    def add_instrument(self, instrument):
        self._instruments.add(instrument)
        if len(self._instruments) == 1:
            self.set_instrument(instrument)
        else:
            for instrument in self._instruments:
                instrument.disarm()
    
    def set_instrument(self, instrument):
        for i in self._instruments:
            i.disarm()
        self.selected_instrument = instrument
        self.selected_instrument.arm()

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


####

NUM_DYNAMIC_ENCODERS = 15

color_letters = [
	'B', #blue
	'p', #pink
	'L', #lavender
	'R', #red
	'G', #green
	'W', #white
	'Y', #gold,
	'O', #orange
	'T', #teal
	'P' #purple
]

color_index_map = {
    9: 'B',
    12: 'p',
    39: 'L',
    56: 'R',
    61: 'G',
    69: 'W',
    13: 'W',
    59: 'Y',
    1: 'O',
    20: 'T',
    24: 'P',
    55: 'W',
    'none': None
}

def get_manual_color(name, instrument):
    if name.startswith('[') and name[1] in color_letters:
        return name[1]
    elif not 'Macro' in name and not 'ctrl_slider' in name:
        return color_index_map[instrument._track.color_index]
    return None

class MFTInput(EbiagiComponent):

    def __init__(self, Set, twister_control):
        super(MFTInput, self).__init__()
        self._set = Set
        self._instruments = set([])

        self.selected_instrument = None

        self.has_audio_input = False
        self.has_midi_input = False

        self.short_name = 'MFT'

        self.log('Initializing MFT Input')
        self.twister_control = twister_control


    def add_instrument(self, instrument):
        self._instruments.add(instrument)
        if len(self._instruments) == 1:
            self.set_instrument(instrument)
        else:
            self.clear()

    def set_instrument(self, instrument):
        self.selected_instrument = instrument
        i = 0
        while i < NUM_DYNAMIC_ENCODERS:
            param = instrument.get_instrument_device().parameters[i+1]
            self.twister_control.assign_encoder(i, param, param.min, param.max, get_manual_color(param.name, instrument))
            i += 1

    def set_global_instrument(self, instrument):
        i = 0
        self.log('whoopie')
        while i < 13:
            self.log('whoopie')
            param = instrument.get_instrument_device().parameters[i+1]
            self.twister_control.assign_encoder(i+16, param, param.min, param.max, get_manual_color(param.name, instrument))
            i += 1

    def clear(self):
        self._instruments = set([])
        i = 0
        while i < NUM_DYNAMIC_ENCODERS:
            self.twister_control.clear_encoder(i)
            i += 1

    def is_active(self):
        return self.selected_instrument != None

    def empty(self):
        return len(self._instruments) == 0
