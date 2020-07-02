from _utils import catch_exception, is_module, is_instrument, is_midi_input, is_audio_input, is_instr, is_loop_track, is_clip_track

class Instrument:

    @catch_exception
    def __init__(self, track, module):
        self.module = module
        self.track = track

        self.midi_inputs = []
        self.audio_inputs = []
        self.nanok_in = None
        self.clip_tracks = []
        self.loop_tracks= []

        tracks = module.set.tracks
        i = tracks.index(track) + 1
        while not is_module(tracks[i]) and not is_instrument(tracks[i]) and tracks[i].is_grouped:
            if is_midi_input(tracks[i], self.module.set.midi_inputs):
                self.midi_inputs.append(tracks[i])
                for routing in tracks[i].available_input_routing_types:
                    if routing.display_name == tracks[i].name.replace('_IN',''):
                        tracks[i].input_routing_type = routing
            if is_audio_input(tracks[i], self.module.set.audio_inputs):
                self.audio_inputs.append(tracks[i])
                for routing in tracks[i].available_input_routing_types:
                    if routing.display_name == tracks[i].name.replace('_IN',''):
                        tracks[i].input_routing_type = routing
            if is_instr(tracks[i]):
                self.instr = tracks[i]
            if is_clip_track(tracks[i]):
                self.clip_tracks.append(tracks[i])
            if is_loop_track(tracks[i]):
                self.loop_tracks.append(tracks[i])
            i += 1

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

    def disarm(self, input_list):
        for track in self.midi_inputs:
            if len(input_list) == 0 or track.name.replace('_IN','') in input_list:
                track.arm = 0

    def activate(self):
        for loop_track in self.loop_tracks:
            if loop_track.can_be_armed:
                loop_track.arm = 1

    def deactivate(self):
        for loop_track in self.loop_tracks:
            if loop_track.can_be_armed:
                loop_track.arm = 0

    def log(self, msg):
        self.module.log(msg)