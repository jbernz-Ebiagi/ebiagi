from _Framework.ControlSurface import get_control_surfaces
from ._EbiagiComponent import EbiagiComponent
from ._naming_conventions import *
from ._Module import Module
from ._Input import Input
from ._Router import Router
from ._Instrument import Instrument
from ._SnapControl import SnapControl
from ._utils import qwerty_order

class Set(EbiagiComponent):

    def __init__(self):
        super(Set, self).__init__()

        self.loading = True
        self.log('Loading Set...')

        self.midi_inputs = []
        self.audio_inputs = []

        self.woot = None

        self.midi_routers = []
        self.audio_routers = []
        
        self.snap_control = None

        self.modules = []
        self.active_module = None

        self.global_instruments = []
        self.global_loop = None
        self.global_loop_track = None

        self.held_instruments = set([])

        self.smart_loop = None

        m = 0
        a = 0

        twister_control = None

        for s in get_control_surfaces():
            if s.__class__.__name__ == 'twister':
                twister_control = s

        for track in self._song.tracks:

            #Add inputs
            if is_input(track.name):
                ipt = Input(track, self)
                if track.has_midi_input:
                    self.midi_inputs.append(ipt)
                    if ipt.short_name == 'WOOT':
                        self.woot = ipt
                    if ipt.short_name == 'MFT1' and twister_control:
                        ipt.update_device = twister_control.set_instrument_dials
                    if ipt.short_name == 'MFT2':
                        ipt.update_device = twister_control.set_fx_dials
                                
                elif track.has_audio_input:
                    self.audio_inputs.append(ipt)

            #Add midi routers       
            if is_midi_router(track.name):
                self.midi_routers.append(Router(track, self)) 
            
            #Add audio routers       
            if is_audio_router(track.name):
                self.audio_routers.append(Router(track, self))

        for track in self._song.tracks:

            #Add Global Instrument
            if is_global_instrument(track.name):
                instr = Instrument(track, self)
                if instr.has_midi_input():
                    instr.set_midi_router(self.midi_routers[m])
                    m += 1
                if instr.has_audio_input():
                    instr.set_audio_router(self.audio_routers[a])
                    a += 1
                self.global_instruments.append(instr)

            #Add Snap Control
            if is_snap_control(track.name):
                sc = SnapControl(track, self)
                sc.set_midi_router(self.midi_routers[m])
                m += 1
                self.snap_control = sc
                if twister_control:
                    twister_control.set_gfx_dial(sc._knob,12)

            #Add global loop
            if is_global_loop_track(track.name):
                self.global_loop_track = track
                self.global_loop = track.clip_slots[0]

        twister_control.set_xfade_dial()

        for track in self._song.tracks:

            #Add modules
            if is_module(track.name):
                module = Module(track, self, m, a)
                self.modules.append(module)
                module.deactivate()

        if len(self.modules):
            self.activate_module(0)
            self.loading = False
            self.message('Loaded Ebiagi Set')

    def activate_module(self, index):
        if self.modules[index]:
            if self.modules[index] != self.active_module:

                if self.active_module:
                    self.active_module.deactivate()

                for router in self.midi_routers and self.audio_routers:
                    router.set_instrument(None)

                for ipt in self.midi_inputs + self.audio_inputs:
                    self.log('clear input')
                    ipt.clear()

                self.modules[index].activate()
                self.active_module = self.modules[index]
                self.smart_loop = None
                self._update_routers()
            else:
                self.message('Module already active')
        else:
            self.log('Module index out of bounds')

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
            instrument = self.active_module.instruments[index]
        self.log(instrument.short_name)
        self.held_instruments.add(instrument)
        instrument.select()
        self._update_routers()

    def deselect_instrument(self, index, instrument=None):
        if not instrument:
            instrument = self.active_module.instruments[index]       
        if instrument in self.held_instruments: 
            self.held_instruments.remove(instrument)
        instrument.deselect()
        self._update_routers()

    def stop_instrument(self, index, instrument=None):
        if not instrument:
            instrument = self.active_module.instruments[index]       
        instrument.stop()

    def select_loop(self, key):
        self.active_module.loops[key].select()

    def deselect_loop(self, key):
        self.active_module.loops[key].deselect()

    def stop_loop(self, key):
        self.active_module.loops[key].stop()

    def stop_all_loops(self):
        for loop in self.active_module.loops.values():
            loop.stop()

    def clear_loop(self, key):
        self.active_module.loops[key].clear()

    def quantize_loop(self, key):
        self.active_module.loops[key].quantize()

    def mute_all_loops(self):
        if self._song.session_record:
            return
        instrs = self.held_instruments if len(self.held_instruments) > 0 else self.active_module.instruments
        for instr in instrs:
            instr.mute_loops()

    def unmute_all_loops(self):
        self.global_loop_track.arm = 1
        for instr in self.active_module.instruments:
            instr.unmute_loops()

    def select_snap(self, index):
        self.snap_control.select_snap(self.active_module.snaps[index])
        self.select_instrument(None, self.snap_control)

    def deselect_snap(self, index):       
        self.deselect_instrument(None, self.snap_control)

    def assign_snap(self, index):
        param = self._song.view.selected_parameter
        track = self._song.view.selected_track
        self.active_module.assign_snap(index, param, track)

    def clear_snap(self, index):
        self.active_module.clear_snap(index)

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
                loop = self.active_module.loops[key]
                if loop and not loop.has_clips():
                    for clip_slot in loop._clip_slots:
                        self.log(clip_slot._instrument.is_selected())
                        if woot.has_instrument(clip_slot._instrument) and clip_slot.will_record_on_start() and not clip_slot._track.playing_slot_index > 0:
                            self.log('select loop')
                            loop.select()
                            self.smart_loop = loop
                            return

    def smart_clear(self):
        if self.smart_loop:
            self.smart_loop.clear()
            self.smart_loop = None

    def clear_arrangement_clip_envelopes(self):
        for instr in self.active_module.instruments:
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


    #TODO: Performance can be improved by mapping names
    def get_scene_index(self, name):
        i = 0
        for scene in self._song.scenes:
            if name == scene.name:
                return i
            i += 1

    def _update_routers(self):
        def update_router(ipt, index):
                if not ipt.empty():
                    if ipt.has_midi_input:
                        for router in self.midi_routers:
                            router.update_input(ipt, index)
                    if ipt.has_audio_input:
                        for router in self.audio_routers:
                            router.update_input(ipt, index)      
        for i, ipt in  enumerate(self.midi_inputs):
            update_router(ipt, i)
        for i, ipt in  enumerate(self.audio_inputs):
            update_router(ipt, i)
     
