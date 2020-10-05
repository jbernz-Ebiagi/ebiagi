from _Instrument import MidiInstrument, AudioInstrument, AuxInstrument, MPEInstrument
from _ModuleFX import ModuleFX
from _Loop import Loop
from _utils import catch_exception, is_module, is_instrument, is_module_fx, is_loop_scene, get_loop_key, set_output_routing, is_mpe_track, is_aux_instrument

class Module:

    @catch_exception
    def __init__(self, track, Set):
        self.set = Set
        self.track = track

        self.instruments = []
        self.main_instruments = []
        self.mfx_instruments = []

        set_output_routing(self.track, 'OUTPUT')

        i = self.set.tracks.index(track) + 1
        a = 0
        m = 0
        while not is_module(self.set.tracks[i]) and self.set.tracks[i].is_grouped:
            if is_instrument(self.set.tracks[i]):
                instrument_track = self.set.tracks[i]
                if instrument_track.has_audio_input:
                    instr = AudioInstrument(instrument_track, self, self.set.audio_channels[a])
                    self.instruments.append(instr)
                    self.main_instruments.append(instr)
                    a += 1
                elif instrument_track.has_midi_input:
                    if is_module_fx(instrument_track):
                        mfx_instrument = MidiInstrument(instrument_track, self, self.set.midi_channels[m])
                        self.instruments.append(mfx_instrument)
                        self.mfx_instruments.append(mfx_instrument)                     
                    if is_aux_instrument(instrument_track):
                        aux_instrument = AuxInstrument(instrument_track, self, self.set.midi_channels[m])
                        self.instruments.append(aux_instrument)
                        self.main_instruments[-1].aux_instruments.append(aux_instrument)
                    elif is_mpe_track(instrument_track):
                        instr = MPEInstrument(instrument_track, self, self.set.midi_channels[m])
                        self.instruments.append(instr)
                        self.main_instruments.append(instr)
                    else:
                        instr = MidiInstrument(instrument_track, self, self.set.midi_channels[m])
                        self.instruments.append(instr)
                        self.main_instruments.append(instr)
                    m += 1
            # if self.set.tracks[i].is_foldable:
            #     self.set.tracks[i].fold_state = 1
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