from _utils import catch_exception

class Input:

    @catch_exception
    def __init__(self, track, set):
        self.set = set
        self.track = track

        self.short_name = track.name.replace('_IN','')

    def get_armed_instruments(self):
        instrs = []
        for channel in self.set.midi_channels + self.set.audio_channels:
            if channel.input_is_armed(self.short_name) and channel.current_instrument:
                instrs.append(channel.current_instrument)
        return instrs


    def log(self, msg):
        self.set.log(msg)