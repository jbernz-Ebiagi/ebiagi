from threading import Timer
from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase
from _utils import catch_exception, is_module, is_input, is_loop_track, get_loop_key, is_loop_scene, is_midi_router, is_audio_router, is_clip_track, is_clip_scene, is_gfx, is_record, is_snap_track
from _Module import Module
from _Loop import Loop
from _Clip import Clip
from _Router import MidiRouter, AudioRouter
from _Input import Input
from _SnapFX import SnapFX

class Set(UserActionsBase):

    def __init__(self, ActionsBase):
        self.base = ActionsBase
        self.tracks = list(self.base.song().tracks)
        self.return_tracks = list(self.base.song().return_tracks)
        self.master_track = self.base.song().master_track
        self.scenes = list(self.base.song().scenes)

        self.modules = []
        self.active_module = None

        self.inputs = {}
        self.output = None
        self.held_instruments = set([])

        self.loops = {}
        self.clips = {}

        self.midi_routers = []
        self.audio_routers = []

        self.global_fx = []
        self.global_loops = []

        self.snap_fx = None

        self.log('Building virtual set...')
        self.loading = True

        #Add audio routers
        for track in self.return_tracks:
            if is_audio_router(track):
                self.audio_routers.append(AudioRouter(track, self))

        channel = 0
        for track in self.tracks:
            #Add inputs
            if is_input(track):
                ipt = Input(track, self)
                self.inputs[track.name.replace('_IN','')] = ipt
                if track.has_midi_output:
                    ipt.set_channel(channel)
                    channel += 1

        for track in self.tracks:

            #Build empty loop structure
            if is_loop_track(track):
                i = 0

                if track.has_midi_output:
                    track.devices[0].parameters[1].value = channel
                    channel += 1

                while i < len(self.scenes):
                    if track.clip_slots[i].has_stop_button:
                        loop_name = get_loop_key(self.scenes[i].name)
                        if not loop_name in self.loops:
                            self.loops[loop_name] = Loop(self, loop_name)
                        if track.has_midi_output:
                            self.loops[loop_name].midi_track = track
                            self.loops[loop_name].midi_clip_slot = track.clip_slots[i]
                        elif track.has_audio_output:
                            self.loops[loop_name].audio_track = track
                            self.loops[loop_name].audio_clip_slot = track.clip_slots[i]
                    i += 1

            if is_clip_track(track):
                i = 0

                if track.has_midi_output:
                    track.devices[0].parameters[1].value = channel
                    channel += 1

                clip_name = None
                while i < len(self.scenes):
                    if self.scenes[i].name == 'STOPCLIP' and track.clip_slots[i].has_clip:
                        if track.has_midi_output:
                            self.clips[clip_name].midi_stop_clip = track.clip_slots[i]
                        elif track.has_audio_output:
                            self.clips[clip_name].audio_stop_clip = track.clip_slots[i]
                    elif track.clip_slots[i].has_stop_button:
                        clip_name = self.scenes[i].name
                        if not clip_name in self.clips:
                            self.clips[clip_name] = Clip(self)
                        if track.has_midi_output:
                            self.clips[clip_name].midi_track = track
                            self.clips[clip_name].midi_clip_slot = track.clip_slots[i]
                        elif track.has_audio_output:
                            self.clips[clip_name].audio_track = track
                            self.clips[clip_name].audio_clip_slot = track.clip_slots[i]
                    i += 1

            #Add modules
            if is_module(track):
                self.modules.append(Module(track, self))

            if is_gfx(track):
                self.global_fx.append(track)

            if is_record(track):
                for clip_slot in track.clip_slots:
                    if clip_slot.has_stop_button:
                        self.global_loops.append(clip_slot)

            if is_snap_track(track):
                self.snap_fx = SnapFX(track, self)

            #Add midi routers
            if is_midi_router(track):
                self.midi_routers.append(MidiRouter(track, self))


        for module in self.modules:
            module.deactivate()
        self.activate_module(0)

        self.setCrossfadeB()

        self.log('...finished building set')
        self.loading = False


    def activate_module(self, index):
        if self.modules[index]:
            if self.modules[index] != self.active_module:

                if self.active_module:
                    self.active_module.deactivate()
                self.clear_loops()
                self.clear_clips()
                self.clear_routers()

                self.modules[index].activate()
                self.map_loops(self.modules[index])
                self.map_clips(self.modules[index])

                self.active_module = self.modules[index]
            else:
                self.log('Module already active')
        else:
            self.log('Module index out of bounds')

    def stop_all_loops(self):
        for key in self.loops:
            self.loops[key].stop()

    def clear_loops(self):
        for key in self.loops:
            self.loops[key].clear()

    def clear_clips(self):
        for key in self.clips:
            self.clips[key].clear()

    def clear_routers(self):
        for router in self.midi_routers:
            router.clear_loops()

    def map_loops(self, module):
        for instrument in module.main_instruments + module.mfx_instruments:
            i = 0
            while i < len(self.scenes):
                if is_loop_scene(self.scenes[i]):
                    key = get_loop_key(self.scenes[i].name)
                    if instrument.has_clip(i):
                        instrument.transfer_clip(self.loops[key], i)
                i += 1

    def map_clips(self, module):
        for instrument in module.main_instruments + module.mfx_instruments:
            i = 0
            while i < len(self.scenes):
                if is_clip_scene(self.scenes[i]):
                    key = self.scenes[i].name
                    if instrument.has_clip(i):
                        instrument.transfer_clip(self.clips[key], i)
                i += 1

    def select_instrument(self, index):
        self.held_instruments.add(self.active_module.main_instruments[index])
        self.arm_instruments_and_fx()

    def deselect_instrument(self, index):
        if self.active_module.main_instruments[index] in self.held_instruments:
            self.held_instruments.remove(self.active_module.main_instruments[index])
        self.arm_instruments_and_fx()

    def stop_instrument(self, index):
        for loop in self.loops:
            if self.loops[loop].instrument is self.active_module.main_instruments[index]:
                self.loops[loop].stop()

    def select_mfx(self, index):
        self.held_instruments.add(self.active_module.mfx_instruments[index])
        self.arm_instruments_and_fx()

    def deselect_mfx(self, index):
        if self.active_module.mfx_instruments[index] in self.held_instruments:
            self.held_instruments.remove(self.active_module.mfx_instruments[index])
        self.arm_instruments_and_fx()

    def select_gfx(self, index):
        self.global_fx[index].arm = 1
        for router in self.midi_routers:
            router.force_disarm('AS')

    def deselect_gfx(self, index):
        self.global_fx[index].arm = 0

    def arm_instruments_and_fx(self):
        for instrument in self.active_module.instruments:
            if instrument in self.held_instruments:
                instrument.arm()
        for instrument in self.active_module.instruments:
            if not instrument in self.held_instruments:
                instrument.disarm()

    def get_arm_count(self, input_name):
        return len(self.inputs[input_name].get_armed_instruments())

    def select_loop(self, name):
        self.loops[name].select()

    def stop_loop(self, name):
        self.loops[name].stop()

    def clear_loop(self, name):
        self.loops[name].clear()

    def play_clip(self, name):
        self.clips[name].play()

    def stop_clip(self, name):
        self.clips[name].stop()

    def select_global_loop(self, index):
        if self.global_loops[index].is_playing:
            self.setCrossfadeA()
        self.global_loops[index].fire()

    def stop_global_loop(self, index):
        self.global_loops[index].stop()

    def clear_global_loop(self, index):
        self.global_loops[index].delete_clip()
        self.setCrossfadeB()

    def setCrossfadeA(self):
        self.master_track.mixer_device.crossfader.value = -1.0

    def setCrossfadeB(self):
        self.master_track.mixer_device.crossfader.value = 1.0

    def recall_snap(self, beats):
        self.snap_fx.recall_snap(beats)

    def select_snap(self, index):
        self.snap_fx.select_snap(self.active_module.snaps[index])
        for router in self.midi_routers:
            router.force_disarm('AS')

    def deselect_snap(self, index):
        self.snap_fx.deselect_snap()

    def assign_snap(self, index):
        param = self.base.song().view.selected_parameter
        track = self.base.song().view.selected_track
        self.snap_fx.assign_snap(self.active_module.snaps[index], param, track)

    def clear_snap(self, index):
        self.active_module.snaps[index] = []
        self.active_module.save_snaps()
        self.message('Cleared snap %s' % str(index+1))

    def toggle_input(self, input_name):
        if input_name == 'LINE':
            if self.inputs['LINE'].track.mute == 0:
                self.inputs['LINE'].track.mute = 1
            else:
                self.inputs['LINE'].track.mute = 0

    def log(self, message):
        self.base.canonical_parent.log_message(message)

    def message(self, message):
        self.base.canonical_parent.show_message(message)