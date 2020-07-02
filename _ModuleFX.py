from _utils import catch_exception, is_module, is_instrument, is_midi_input, is_instr, is_loop_track, is_clip_track

class ModuleFX:

    @catch_exception
    def __init__(self, track, module):
        self.module = module
        self.track = track
        for routing in self.track.available_input_routing_types:
            if routing.display_name == 'AS':
                self.track.input_routing_type = routing

    def arm(self, input_list):
        self.track.arm = 1

    def disarm(self, input_list):
        self.track.arm = 0

    def log(self, msg):
        self.module.log(msg)