from _Instrument import MidiInstrument, AudioInstrument, AuxInstrument
from _Loop import Loop
from _utils import catch_exception, is_module, is_instrument, is_module_fx, is_loop_scene, get_loop_key, set_output_routing, is_aux_instrument

class Module:

    @catch_exception
    def __init__(self, track, Set):
        self.set = Set
        self.track = track

        self.instruments = []
        self.main_instruments = []
        self.mfx_instruments = []

        self.snaps = self.track.get_data('snaps', False)
        if not self.snaps:
            self.snaps = [[],[],[],[],[],[]]
        self.log(self.snaps)

        set_output_routing(self.track, 'OUTPUT')

        i = self.set.tracks.index(track) + 1
        a = 0
        m = 0
        while not is_module(self.set.tracks[i]) and self.set.tracks[i].is_grouped:

            if is_instrument(self.set.tracks[i]):
                instrument_track = self.set.tracks[i]
                if instrument_track.has_audio_input:
                    instr = AudioInstrument(instrument_track, self, self.set.audio_routers[a])
                    self.instruments.append(instr)
                    self.main_instruments.append(instr)
                    a += 1
                elif instrument_track.has_midi_input:
                    if is_module_fx(instrument_track):
                        mfx_instrument = MidiInstrument(instrument_track, self, self.set.midi_routers[m])
                        self.instruments.append(mfx_instrument)
                        self.mfx_instruments.append(mfx_instrument)                     
                    elif is_aux_instrument(instrument_track):
                        aux_instrument = AuxInstrument(instrument_track, self, self.set.midi_routers[m])
                        self.instruments.append(aux_instrument)
                        self.main_instruments[-1].aux_instruments.append(aux_instrument)
                    else:
                        instr = MidiInstrument(instrument_track, self, self.set.midi_routers[m])
                        self.instruments.append(instr)
                        self.main_instruments.append(instr)
                    m += 1

            for snap in self.snaps:
                for snap_param in snap:
                    if snap_param['track_name'] == self.set.tracks[i].name:
                        snap_param['param'] = self.set.tracks[i].devices[0].parameters[snap_param['index']]
            
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

    def mute_all_loops(self):
        for instrument in self.instruments:
            instrument.mute_loops()

    def unmute_all_loops(self):
        for instrument in self.instruments:
            instrument.unmute_loops()

    def save_snaps(self):
        saveable_snaps = [[],[],[],[],[],[]]
        i = 0
        for snap in self.snaps:
            for snap_param in snap:
                saveable_snaps[i].append({
                    'value': snap_param['value'],
                    'track_name': snap_param['track_name'],
                    'index': snap_param['index']
                })
            i += 1
        self.track.set_data('snaps', saveable_snaps)
        self.log(self.track.get_data('snaps', False))

    def log(self, msg):
        self.set.log(msg)