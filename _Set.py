from threading import Timer
from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase
from _utils import catch_exception, is_module, is_record, is_gfx
from _Module import Module

class Set(UserActionsBase):

    def __init__(self, ActionsBase):
        self.base = ActionsBase
        self.tracks = list(self.base.song().tracks)
        self.scenes = list(self.base.song().scenes)
        self.modules = []
        self.active_module = None
        self.global_loops = []
        self.global_fx = []
        self.held_gfx = set([])

        self.log('Building virtual set...')

        #TODO make inputs dynamic
        self.midi_inputs = ['CBORD', 'AS', 'NANOK']
        self.audio_inputs = ['LINE']
        self.held_inputs = set([])

        for track in self.tracks:
            if is_module(track):
                self.modules.append(Module(track, self))
            if is_record(track):
                for clip_slot in track.clip_slots:
                    if clip_slot.has_stop_button:
                        self.global_loops.append(clip_slot)
            if is_gfx(track):
                self.global_fx.append(track)

        self.activate_module(0)


    def activate_module(self, index):
        if self.modules[index]:
            if self.modules[index] != self.active_module:
                if self.active_module:
                    self.active_module.stop_all_loops()
                for module in self.modules:
                    module.deactivate()
                self.modules[index].activate()
                self.active_module = self.modules[index]
            else:
                self.log('Module already active')
        else:
            self.log('Module index out of bounds')

    def arm_instruments_and_fx(self):
        for instrument in self.active_module.instruments:
            if instrument in self.active_module.held_instruments:
                instrument.arm(self.held_inputs)
            else:
                instrument.disarm(self.held_inputs)
        for mfx in self.active_module.module_fx:
            if mfx in self.active_module.held_mfx:
                mfx.arm(self.held_inputs)
            else:
                mfx.disarm(self.held_inputs)
        for gfx in self.global_fx:
            if gfx in self.held_gfx:
                gfx.arm = 1
            else:
                gfx.arm = 0

    def select_input(self, name):
        self.held_inputs.add(name)

    def deselect_input(self, name):
        self.held_inputs.remove(name)

    def toggle_input(self, name):
        self.active_module.toggle_input(name)

    def clear_module(self, index):
        if self.modules[index]:
            self.modules[index].clear_all_loops()

    def select_global_loop(self, index):
        self.global_loops[index].fire()

    def stop_global_loop(self, index):
        self.global_loops[index].stop()

    def clear_global_loop(self, index):
        self.global_loops[index].delete_clip()

    def select_gfx(self, index):
        self.held_gfx.add(self.global_fx[index])
        self.select_input('AS')
        self.arm_instruments_and_fx()
        self.deselect_input('AS')

    def deselect_gfx(self, index):
        self.held_gfx.remove(self.global_fx[index])
        self.select_input('AS')
        self.arm_instruments_and_fx()
        self.deselect_input('AS')

    def log(self, message):
        self.base.canonical_parent.log_message(message)