from _utils import catch_exception, set_input_routing

class Channel:

    @catch_exception
    def __init__(self, track, Set):
        self.set = Set
        self.track = track

        self.current_instrument = None

    def log(self, msg):
        self.module.log(msg)

    def assign(self, instrument):
        for chain in self.track.devices[0].chains:
            if chain.name == 'LOOP' or chain.name in instrument.input_names:
                chain.mute = 0
            else:
                chain.mute = 1

    def clear(self):
        for chain in self.track.devices[0].chains:
            if chain.name == 'LOOP':
                chain.mute = 0
            else:
                chain.mute = 1