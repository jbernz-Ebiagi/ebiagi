from _utils import catch_exception, set_input_routing

class Router:

    @catch_exception
    def __init__(self, track, Set):
        self.set = Set
        self.track = track

        self.current_instrument = None
        self.input_device = None
        self.loop_device = None

        for chain in self.track.devices[0].chains:
            if chain.name == 'INPUTS':
                if len(chain.devices) > 0:
                    self.input_device = chain.devices[0]
            if chain.name == 'LOOPS':
                if len(chain.devices) > 0:
                    self.loop_device = chain.devices[0]
                    self.clear_loops()


    def arm(self, input_names):
        for chain in self.input_device.chains:
            if chain.name in input_names:
                chain.mute = 0
            else:
                chain.mute = 1

    def disarm(self):
        for chain in self.input_device.chains:
            #Lazy disarming
            if chain.mute == 0 and self.set.get_arm_count(chain.name) < 2:
                chain.mute = 0
            else:
                chain.mute = 1

    def force_disarm(self, input_name):
        for chain in self.input_device.chains:
            if chain.name == input_name:
                chain.mute = 1

    def input_is_armed(self, input_name):
        for chain in self.input_device.chains:
            if chain.name == input_name:
                return chain.mute == 0
        return False

    def unmute_loops(self):
        for chain in self.track.devices[0].chains:
            if chain.name == 'LOOPS':
                chain.mute = 0

    def mute_loops(self):
        for chain in self.track.devices[0].chains:
            if chain.name == 'LOOPS':
                chain.mute = 1

    def log(self, msg):
        self.set.log(msg)


class AudioRouter(Router):

    @catch_exception
    def __init__(self, track, Set):
        Router.__init__(self, track, Set)

class MidiRouter(Router):

    @catch_exception
    def __init__(self, track, Set):
        Router.__init__(self, track, Set)
        self.loop_history = [0,0,0,0,0,0,0,0]

        for ipt in self.set.inputs:
            for parameter in self.input_device.parameters:
                if parameter.name == ipt:
                    parameter.value = self.set.inputs[ipt].channel

    def add_loop(self, channel):
        i = 1
        o = i
        while i < 9:
            if self.loop_device.parameters[i].value == channel:
                return
            elif self.loop_device.parameters[i].value == 127 or self.loop_history[i-1] > self.loop_history[o-1]:
                o = i
            i += 1
        self.loop_device.parameters[o].value = channel
        self.loop_history[o-1] = 0

    def deactivate_loop(self, channel):
        i = 1
        while i < 9:
            if self.loop_device.parameters[i].value == channel or self.loop_device.parameters[i].value > 0:
                self.loop_history[i-1] += 1
            i += 1

    def clear_loops(self):
        i = 1
        self.loop_history = [0,0,0,0,0,0,0,0]   

        while i < 9:
            self.loop_device.parameters[i].value = 127
            self.loop_device.chains[i-1].color_index = 55
            self.loop_history[i-1] = 0
            i += 1
