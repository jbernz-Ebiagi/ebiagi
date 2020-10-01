from _Instrument import Instrument, MidiInstrument, AudioInstrument, MPEInstrument
from _ModuleFX import ModuleFX
from _Loop import Loop
from _utils import catch_exception, is_module, is_instrument, is_module_fx, is_loop_scene, get_loop_key, set_output_routing, is_mpe_track

class Module:

    @catch_exception
    def __init__(self, track, Set):
        self.set = Set
        self.track = track

        self.instruments = []

        set_output_routing(self.track, 'OUTPUT')

        i = self.set.tracks.index(track) + 1
        a = 0
        m = 0
        while not is_module(self.set.tracks[i]) and self.set.tracks[i].is_grouped:
            if is_instrument(self.set.tracks[i]):
                if self.set.tracks[i].has_audio_input:
                    self.instruments.append(AudioInstrument(self.set.tracks[i], self, self.set.audio_channels[a]))
                    a += 1
                if self.set.tracks[i].has_midi_input:
                    if is_mpe_track(self.set.tracks[i]):
                        self.instruments.append(MPEInstrument(self.set.tracks[i], self, self.set.midi_channels[m]))
                    else:
                        self.instruments.append(MidiInstrument(self.set.tracks[i], self, self.set.midi_channels[m]))
                    m += 1
            elif is_mpe_track(self.set.tracks[i]):
                self.instruments[-1].mpe_tracks.append(self.set.tracks[i])
            if self.set.tracks[i].is_foldable:
                self.set.tracks[i].fold_state = 1
            i += 1

    def activate(self):
        self.log('activate ' + self.track.name)
        for instrument in self.instruments:
            instrument.activate()
        self.track.fold_state = 0
        self.track.mute = 0

    def deactivate(self):
        self.log('deactivate ' + self.track.name)
        for instrument in self.instruments:
            instrument.deactivate()
        self.track.fold_state = 1
        self.track.mute = 1

    def log(self, msg):
        self.set.log(msg)