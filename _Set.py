from ._EbiagiComponent import EbiagiComponent
from ._naming_conventions import *
from ._Module import Module
from ._Input import Input, MFTInput
from ._Instrument import Instrument
from ._SnapControl import SnapControl
from ._utils import qwerty_order

class Set(EbiagiComponent):

    def __init__(self, twister_control):
        super(Set, self).__init__()

        self.loading = True
        self.log('Loading Set...')

        self.midi_inputs = []
        self.audio_inputs = []

        self.woot = None
        
        self.snap_control = None

        self.modules = []
        self.active_modules = {
            'A': None,
            'B': None
        }
        self.targetted_module = None

        self.global_instruments = []
        self.global_loop = None
        self.global_loop_track = None

        self.held_instruments = set([])

        self.smart_loop = None

        self.crossfade_module = None
        self.active_crossfade = False

        m = 0
        a = 0

        self.twister_control = twister_control
        
        tempo = self.song().master_track.mixer_device.song_tempo
        self.twister_control.assign_encoder(31, tempo, 126, 144, 'G')

        self.mft_input = MFTInput(self, self.twister_control)

        for track in self._song.tracks:

            #Add inputs
            if is_input(track.name):
                ipt = Input(track, self)
                if track.has_midi_input:
                    self.midi_inputs.append(ipt)
                    if ipt.short_name == 'WOOT':
                        self.woot = ipt
                elif track.has_audio_input:
                    self.audio_inputs.append(ipt)

        for track in self._song.tracks:

            #Add Global Instrument
            if is_global_instrument(track.name):
                instr = Instrument(track, self)
                if instr.short_name == 'SFX':
                    self.mft_input.set_global_instrument(instr)
                self.global_instruments.append(instr)

            # #Add Snap Control
            # if is_snap_control(track.name):
            #     sc = SnapControl(track, self)
            #     m += 1
            #     self.snap_control = sc
            #     if self.twister_control:
            #         self.twister_control.assign_encoder(15, sc._knob, sc._knob.min, sc._knob.max, 'B')

            #Add global loop
            if is_global_loop_track(track.name):
                self.global_loop_track = track
                self.global_loop = track.clip_slots[0]

        # twister_control.set_xfade_dial()

        for track in self._song.tracks:

            #Add modules
            if is_module(track.name):
                module = Module(track, self, m, a)
                self.modules.append(module)
                module.deactivate()

        if len(self.modules):
            self.assign_module(0,'A')
            self.active_modules['A']._track.mixer_device.volume.value = 0.8
            self.loading = False
            self.message('Loaded Ebiagi Set')

    def assign_module(self, index, slot):

        if self.active_modules[slot] != None:
            self.message('Clear slot before assigning module')
            return

        if self.modules[index]:
            if self.modules[index] != self.active_modules['A'] and self.modules[index] != self.active_modules['B']:
                self.modules[index].activate()
                self.active_modules[slot] = self.modules[index]
                volume = self.active_modules[slot]._track.mixer_device.volume
                if slot == 'A':
                    self.twister_control.assign_encoder(29, volume, volume.min, 0.8, 'R')
                else:
                    self.twister_control.assign_encoder(30, volume, volume.min, 0.8, 'R')
                self.target_module(slot)
            else:
                self.message('Module already active')
        else:
            self.log('Module index out of bounds')

    def target_module(self, slot):
        if self.targetted_module is not self.active_modules[slot]:

            for ipt in self.midi_inputs + self.audio_inputs:
                ipt.clear()
            
            self.smart_loop = None

            if self.targetted_module is not None:
                self.targetted_module.fold()

            self.targetted_module = self.active_modules[slot]
            self.targetted_module.unfold()
            self.select_instrument(0)
            self.deselect_instrument(0)

    def clear_module(self, slot):
        #if volume is 0 return error
        if self.active_modules[slot]._track.mixer_device.volume.value != self.active_modules[slot]._track.mixer_device.volume.min:
            self.message('Set volume to 0 before clearing')
            return
        if self.active_modules[slot] is self.targetted_module:
            if slot == 'A':
                self.target_module('B')
            else:
                self.target_module('A')
        self.active_modules[slot].deactivate()
        self.active_modules[slot] = None
        if slot == 'A':
            self.twister_control.clear_encoder(13)
        else:
            self.twister_control.clear_encoder(14)

    def toggle_input(self, key):
        for ipt in self.midi_inputs + self.audio_inputs:
            if ipt.short_name == key:
                ipt.toggle()

    def get_input(self, key):
        for ipt in self.midi_inputs + self.audio_inputs:
            if ipt.short_name == key:
                return ipt
        return False

    def select_instrument(self, index, instrument=None):
        if not instrument:
            instrument = self.targetted_module.instruments[index]
        self.held_instruments.add(instrument)
        if len(self.held_instruments) == 1:
            instrument.select()
            #always assign mft to selected instrument
            self.mft_input.set_instrument(instrument)

    def deselect_instrument(self, index, instrument=None):
        if not instrument:
            instrument = self.targetted_module.instruments[index]       
        if instrument in self.held_instruments: 
            self.held_instruments.remove(instrument)
        #instrument.deselect()

    def stop_instrument(self, index, instrument=None):
        if not instrument:
            instrument = self.targetted_module.instruments[index]       
        instrument.stop()

    def select_loop(self, key):
        self.targetted_module.loops[key].select()

    def deselect_loop(self, key):
        self.targetted_module.loops[key].deselect()

    def stop_loop(self, key):
        self.targetted_module.loops[key].stop()

    def stop_all_loops(self):
        for loop in list(self.targetted_module.loops.values()) + self.targetted_module.variations:
            loop.stop()

    def clear_loop(self, key):
        self.targetted_module.loops[key].clear()

    def quantize_loop(self, key):
        self.targetted_module.loops[key].quantize()

    def mute_all_loops(self):
        if self._song.session_record:
            return
        instrs = self.held_instruments if len(self.held_instruments) > 0 else self.targetted_module.instruments
        for instr in instrs:
            instr.mute_loops()

    def unmute_all_loops(self):
        # self.global_loop_track.arm = 1
        for instr in self.targetted_module.instruments:
            instr.unmute_loops()

    def select_snap(self, index):
        self.snap_control.select_snap(self.targetted_module.snaps[index])

    def deselect_snap(self, index):       
        #do nothing
        self.log('')

    def assign_snap(self, index):
        param = self._song.view.selected_parameter
        track = self._song.view.selected_track
        self.targetted_module.assign_snap(index, param, track)

    def clear_snap(self, index):
        self.targetted_module.clear_snap(index)

    def recall_snap(self, beats):
        self.snap_control.ramp(beats)

    def select_global_instrument(self, index):
        self.select_instrument(None, self.global_instruments[index])

    def deselect_global_instrument(self, index):
        self.deselect_instrument(None, self.global_instruments[index])

    def select_global_loop(self):
        if self.global_loop.is_playing:
            self.setCrossfadeA()
        self.global_loop.fire()

    def stop_global_loop(self):
        self.global_loop.stop()

    def clear_global_loop(self):
        self.global_loop.delete_clip()
        self.setCrossfadeB()

    def setCrossfadeA(self):
        self._song.master_track.mixer_device.crossfader.value = -1.0

    def setCrossfadeB(self):
        self._song.master_track.mixer_device.crossfader.value = 1.0

    def toggle_metronome(self):
        self._song.metronome = not self._song.metronome

    def smart_record(self):
        if self.smart_loop and self.smart_loop.is_recording():
            self.smart_loop.select()
        else:
            woot = self.woot
            for key in qwerty_order:
                loop = self.targetted_module.loops[key]
                if loop and not loop.has_clips():
                    for clip_slot in loop._clip_slots:
                        if woot.has_instrument(clip_slot._instrument) and clip_slot.will_record_on_start() and not clip_slot._track.playing_slot_index > 0:
                            loop.select()
                            self.smart_loop = loop
                            return

    def smart_clear(self):
        if self.smart_loop:
            self.smart_loop.clear()
            self.smart_loop = None

    def clear_arrangement_clip_envelopes(self):
        for instr in self.targetted_module.instruments:
            instr.clear_arrangement_envelopes()

    ## TODO: implement this in a more extensible/less brittle way
    def woot_arp_on(self, args):
        dev = self.woot._track.devices[0]
        for param in dev.parameters:
            if param.name == 'Device On':
                param.value = param.max
            # if param.name == 'Sync On':
            #     if args == 'free':
            #         param.value = param.min
            #     else:
            #         param.value = param.max
            # if param.name == 'Synced Rate':
            #     self.log(param.value_items)
            #     if args in param.value_items:
            #         param.value = args

    def woot_arp_off(self):
        dev = self.woot._track.devices[0]
        for param in dev.parameters:
            if param.name == 'Device On':
                param.value = param.min

    def woot_arp_style(self):
        dev = self.woot._track.devices[0]
        for param in dev.parameters:
            if param.name == 'Style':
                param.value = args


    # def start_crossfade(self):
    #     if self.active_crossfade:
    #         if self.crossfade_module:
    #             self.crossfade_module.deactivate()
    #             self.crossfade_module.clearCrossfade()
    #             self.crossfade_module = None
    #         self.targetted_module.clearCrossfade()
    #     self.setCrossfadeA()
    #     self.active_crossfade = not self.active_crossfade

    #TODO: Performance can be improved by mapping names
    def get_scene_index(self, name):
        i = 0
        for scene in self._song.scenes:
            if name == scene.name:
                return i
            i += 1

    def disconnect(self):
        super(Set, self).disconnect()
        for module in self.modules:
            module.disconnect()
        # self.snap_control.disconnect()