from threading import Timer
from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase
from _utils import catch_exception, is_module, is_input, is_loop_track, get_loop_key, is_loop_scene, is_midi_channel, is_audio_channel, is_mpe_loop 
from _Module import Module
from _Loop import Loop
from _Channel import Channel

class Set(UserActionsBase):

    def __init__(self, ActionsBase):
        self.base = ActionsBase
        self.tracks = list(self.base.song().tracks)
        self.return_tracks = list(self.base.song().return_tracks)
        self.scenes = list(self.base.song().scenes)

        self.modules = []
        self.active_module = None

        self.inputs = []
        self.output = None

        self.loops = {}
        self.clips = {}

        self.midi_channels = []
        self.audio_channels = []

        self.log('Building virtual set...')

        #Add audio channels
        for track in self.return_tracks:
            if is_audio_channel(track):
                self.audio_channels.append(Channel(track, self))

        for track in self.tracks:

            #Add modules
            if is_module(track):
                self.modules.append(Module(track, self))

            #Add inputs
            if is_input(track):
                self.inputs.append(track)

            #Build empty loop structure
            if is_loop_track(track) or is_mpe_loop(track):
                i = 0
                while i < len(self.scenes):
                    if track.clip_slots[i].has_stop_button:
                        loop_name = get_loop_key(self.scenes[i].name)
                        if not loop_name in self.loops:
                            self.loops[loop_name] = Loop(self)
                        if is_mpe_loop(track):
                            self.loops[loop_name].mpe_tracks.append(track)
                            self.loops[loop_name].mpe_clip_slots.append(track.clip_slots[i])
                        elif track.has_midi_output:
                            self.loops[loop_name].midi_track = track
                            self.loops[loop_name].midi_clip_slot = track.clip_slots[i]
                        elif track.has_audio_output:
                            self.loops[loop_name].audio_track = track
                            self.loops[loop_name].audio_clip_slot = track.clip_slots[i]
                    i += 1

            #Add midi channels
            if is_midi_channel(track):
                self.midi_channels.append(Channel(track, self))


        for module in self.modules:
            module.deactivate()
        self.activate_module(0)


    def activate_module(self, index):
        if self.modules[index]:
            if self.modules[index] != self.active_module:

                if self.active_module:
                    self.active_module.deactivate()
                    self.clear_loops()

                self.modules[index].activate()
                self.map_loops(self.modules[index])

                self.active_module = self.modules[index]
            else:
                self.log('Module already active')
        else:
            self.log('Module index out of bounds')

    def clear_loops(self):
        for key in self.loops:
            self.loops[key].clear_clips()
            self.loops[key].clear_instrument()

    def map_loops(self, module):
        for instrument in module.instruments:
            self.log(instrument.track.name)
            i = 0
            while i < len(self.scenes):
                if is_loop_scene(self.scenes[i]):
                    key = get_loop_key(self.scenes[i].name)
                    if instrument.has_clip(i):
                        instrument.transfer_clip(self.loops[key], i)
                i += 1


    def log(self, message):
        self.base.canonical_parent.log_message(message)