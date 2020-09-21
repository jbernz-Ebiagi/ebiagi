import math
from _Scheduler import schedule
from _utils import catch_exception, get_loop_key, is_module, is_instrument, is_midi_input, is_audio_input, is_instr, is_loop_track, is_clip_track, set_input_routing, is_mpe_track, set_mpe_output_channel

class Instrument:

    @catch_exception
    def __init__(self, track, module):
        self.module = module
        self.track = track

        self.midi_inputs = []
        self.audio_inputs = []
        self.nanok_in = None
        self.clip_tracks = []
        self.clips = {}
        self.loop_tracks = []
        self.params = []

        tracks = module.set.tracks
        i = tracks.index(track) + 1
        while not is_module(tracks[i]) and not is_instrument(tracks[i]) and tracks[i].is_grouped:
            if is_midi_input(tracks[i], self.module.set.midi_inputs):
                self.midi_inputs.append(tracks[i])
                set_input_routing(tracks[i], tracks[i].name.replace('_IN',''))
            if is_audio_input(tracks[i], self.module.set.audio_inputs):
                self.audio_inputs.append(tracks[i])
                set_input_routing(tracks[i], tracks[i].name.replace('_IN',''))
                tracks[i].input_routing_channel = tracks[i].available_input_routing_channels[1]
            if is_instr(tracks[i]):
                self.instr = tracks[i]
            if is_clip_track(tracks[i]):
                self.clip_tracks.append(tracks[i])
            if is_loop_track(tracks[i]):
                self.loop_tracks.append(tracks[i])
            if is_mpe_track(tracks[i]):
                set_mpe_output_channel(tracks[i])
            i += 1


        scenes = module.set.scenes
        i = 0
        stop_clip_index = None
        for scene in scenes:
            if scene.name == 'STOPCLIP':
                stop_clip_index = i
            i += 1
        i = 0
        for scene in scenes:
            self.clips[scene.name] = {
                'play': [],
                'stop': []
            }
            for clip_track in self.clip_tracks:
                if clip_track.clip_slots[i].has_clip:
                    self.clips[scene.name]['play'].append(clip_track.clip_slots[i])
                    self.clips[scene.name]['stop'].append(clip_track.clip_slots[stop_clip_index])
            i += 1

        self.set_params()
            

    def get_input(self, input_name):
        for track in self.midi_inputs + self.audio_inputs:
            if input_name + '_IN' == track.name:
                return track
        return False

    def toggle_input(self, input_name):
        for track in self.midi_inputs + self.audio_inputs:
            if input_name + '_IN' == track.name:
                track.arm = 0 if track.arm else 1

    def arm(self, input_list):
        for track in self.midi_inputs:
            if len(input_list) == 0 or track.name.replace('_IN','') in input_list:
                track.arm = 1
        #self.module.set.base.song().view.selected_track = self.instr
        #self.module.set.base.canonical_parent.application().view.show_view('Detail/DeviceChain')

    def disarm(self, input_list):
        for track in self.midi_inputs:
            if len(input_list) == 0 or track.name.replace('_IN','') in input_list:
                track.arm = 0

    def is_armed(self):
        for track in self.midi_inputs + self.audio_inputs:
            if track.arm == 1:
                return True
        return False

    def stop(self):
        self.track.stop_all_clips()

    def activate(self):
        for loop_track in self.loop_tracks:
            if loop_track.can_be_armed:
                loop_track.arm = 1
        if self.instr.devices[0]:
           self.instr.devices[0].parameters[0].value = 1

    def deactivate(self):
        for loop_track in self.loop_tracks:
            if loop_track.can_be_armed:
                loop_track.arm = 0
        if self.instr.devices[0]:
           self.instr.devices[0].parameters[0].value = 0

    def mute_loops(self):
        self.log('mute')
        for track in self.loop_tracks:
            self.log(track)
            self.log(track.mute)
            track.mute = 1

    def unmute_loops(self):
        self.log('unmute')
        for track in self.loop_tracks:
            self.log(track)
            track.mute = 0

    def play_clip(self, name):
        nanok_in = self.get_input('NANOK')
        if (nanok_in and nanok_in.arm) or not nanok_in:
            for clip_slot in self.clips[name]['play']:
                clip_slot.fire()

                if 'GATE' in clip_slot.clip.name:
                    self.mute_loops()

    def stop_clip(self, name):
        nanok_in = self.get_input('NANOK')
        if (nanok_in and nanok_in.arm) or not nanok_in:
            for clip_slot in self.clips[name]['stop']:
                clip_slot.fire()
            for clip_slot in self.clips[name]['play']:
                if 'GATE' in clip_slot.clip.name:
                    self.unmute_loops()

    def shift_preset(self, direction):
        if self.instr.devices[0] and self.instr.devices[0].can_have_chains:
            chains = list(self.instr.devices[0].chains)
            if len(chains) > 1:
                newValue = int(self.instr.devices[0].parameters[1].value + direction)
                if newValue < 0:
                    newValue = len(chains) - 1
                elif newValue > len(chains) - 1:
                    newValue = 0
                self.instr.devices[0].parameters[1].value = newValue
                self.instr.devices[0].view.selected_chain = chains[newValue]

    def set_params(self):
        i = 0
        self.params = []
        while i < 8:
            self.params.append(self.instr.devices[0].parameters[i+1].value)
            i+=1

    def reset_params(self):
        i = 0
        while i < 8:
            if self.instr.devices[0].parameters[i+1].is_enabled:
                self.instr.devices[0].parameters[i+1].value = self.params[i]
            i+=1

    def log(self, msg):
        self.module.log(msg)