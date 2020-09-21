from _utils import catch_exception, is_module, is_instrument, is_midi_input, is_instr, is_loop_track, is_clip_track

class ModuleFX:

    @catch_exception
    def __init__(self, track, module):
        self.module = module
        self.track = track
        self.clips = {}
        for routing in self.track.available_input_routing_types:
            if routing.display_name == 'AS':
                self.track.input_routing_type = routing

        stop_clip_index = None
        i = 0
        for scene in module.set.scenes:
            if scene.name == 'STOPCLIP':
                stop_clip_index = i
            i += 1
        i = 0
        for scene in module.set.scenes:
            self.clips[scene.name] = {
                'play': [],
                'stop': []
            }
            if track.clip_slots[i].has_clip:
                self.clips[scene.name]['play'].append(track.clip_slots[i])
                self.clips[scene.name]['stop'].append(track.clip_slots[stop_clip_index])
            i += 1

    def arm(self, input_list):
        self.track.arm = 1

    def disarm(self, input_list):
        self.track.arm = 0

    def activate(self):
        if self.track.devices[0]:
           self.track.devices[0].parameters[0].value = 1

    def deactivate(self):
        if self.track.devices[0]:
           self.track.devices[0].parameters[0].value = 0

    def play_clip(self, name):
        for clip_slot in self.clips[name]['play']:
            clip_slot.fire()

            if 'GATE' in clip_slot.clip.name:
                self.mute_loops()

    def stop_clip(self, name):
        for clip_slot in self.clips[name]['stop']:
            clip_slot.fire()
        for clip_slot in self.clips[name]['play']:
            if 'GATE' in clip_slot.clip.name:
                self.unmute_loops()
           
    def log(self, msg):
        self.module.log(msg)