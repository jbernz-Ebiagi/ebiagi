from _Instrument import Instrument
from _ModuleFX import ModuleFX
from _Loop import Loop
from _utils import catch_exception, is_module, is_instrument, is_module_fx, is_loop_scene, get_loop_key, set_output_routing

class Module:

    @catch_exception
    def __init__(self, track, Set):
        self.set = Set
        
        self.track = track
        self.instruments = []
        self.held_instruments = set([])
        self.module_fx = []
        self.held_mfx = set([])
        self.loops = {}

        set_output_routing(self.track, 'OUTPUT')

        i = self.set.tracks.index(track) + 1
        while not is_module(self.set.tracks[i]) and self.set.tracks[i].is_grouped:
            if is_instrument(self.set.tracks[i]):
                instrument = Instrument(self.set.tracks[i], self)
                self.instruments.append(instrument)
            if is_module_fx(self.set.tracks[i]):
                mfx = ModuleFX(self.set.tracks[i], self)
                self.module_fx.append(mfx)
            i += 1

        s = 0
        scenes = self.set.scenes
        while s < len(scenes):
            if is_loop_scene(scenes[s]):
                instr_clip_slots = []
                for instrument in self.instruments:
                    for clip_track in instrument.clip_tracks:
                        instr_clip_slots.append({
                            'clip_slot': clip_track.clip_slots[s],
                            'instrument': instrument,
                            'track': clip_track,
                            'mfx': None
                        })
                    for loop_track in instrument.loop_tracks:
                        instr_clip_slots.append({
                            'clip_slot': loop_track.clip_slots[s],
                            'instrument': instrument,
                            'mfx': None,
                            'track': loop_track
                        })
                for mfx in self.module_fx:
                    instr_clip_slots.append({
                        'clip_slot': mfx.track.clip_slots[s],
                        'mfx': mfx,
                        'instrument': None,
                        'track': mfx.track
                    })

                self.loops[get_loop_key(scenes[s].name)] = Loop(track.clip_slots[s], instr_clip_slots, self)
            s += 1

    def select_instrument(self, index):
        self.held_instruments.add(self.instruments[index])
        self.set.arm_instruments_and_fx()

    def deselect_instrument(self, index):
        if self.instruments[index] in self.held_instruments:
            self.held_instruments.remove(self.instruments[index])
        if len(self.held_instruments) + len(self.held_mfx) > 0:
            self.set.arm_instruments_and_fx()

    def select_mfx(self, index):
        self.held_mfx.add(self.module_fx[index])
        self.select_input('AS')       
        self.set.arm_instruments_and_fx()
        self.deselect_input('AS')

    def deselect_mfx(self, index):
        if self.module_fx[index] in self.held_mfx:
            self.held_mfx.remove(self.module_fx[index])
        if len(self.held_instruments) + len(self.held_mfx) > 0:
            self.set.select_input('AS')
            self.set.arm_instruments_and_fx()
            self.set.deselect_input('AS')

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

    def select_loop(self, name):
        self.loops[name].select()

    def deselect_loop(self, name):
        self.loops[name].deselect()

    def stop_loop(self, name):
        self.loops[name].stop()

    def stop_all_loops(self):
        for loop in self.loops:
            self.loops[loop].stop()

    def clear_loop(self, name):
        self.loops[name].clear()

    def clear_all_loops(self):
        for loop in self.loops:
            self.loops[loop].clear()

    def quantize_loop(self, name):
        self.loops[name].quantize()

    def toggle_input(self, name):
        for instrument in self.instruments:
            instrument.toggle_input(name)

    def log(self, msg):
        self.set.log(msg)