from _utils import catch_exception

class Input:

    @catch_exception
    def __init__(self, track, set):
        self.set = set
        self.track = track
        self.channel = None
        self.short_name = track.name.replace('_IN','')

    def get_armed_instruments(self):
        instrs = []
        for router in self.set.midi_routers + self.set.audio_routers:
            if router.input_is_armed(self.short_name) and router.current_instrument:
                instrs.append(router.current_instrument)
        return instrs

    def set_channel(self, channel):
        self.channel = channel
        if self.track.has_midi_output:
            self.track.devices[0].parameters[1].value = channel


    def log(self, msg):
        self.set.log(msg)