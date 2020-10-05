from _utils import catch_exception, set_input_routing

class Channel:

    @catch_exception
    def __init__(self, track, Set):
        self.set = Set
        self.track = track

        self.current_instrument = None

    def disarm(self):
        for chain in self.track.devices[0].chains:
            if chain.name == 'LOOP':
                chain.mute = 0
            else:
                # chain.mute = 1
                # #lazy disarming
                if chain.mute == 0 and self.set.get_arm_count(chain.name) < 2:
                    chain.mute = 0
                else:
                    chain.mute = 1

    def arm(self, input_names):
        for chain in self.track.devices[0].chains:
            if chain.name == 'LOOP' or chain.name in input_names:
                chain.mute = 0
            else:
                chain.mute = 1

    def input_is_armed(self, input_name):
        for chain in self.track.devices[0].chains:
            if chain.name == input_name:
                return chain.mute == 0
        return False

    def mute_as(self):
        for chain in self.track.devices[0].chains:
            if chain.name == 'AS':
                chain.mute = 1

    def log(self, msg):
        self.module.log(msg)