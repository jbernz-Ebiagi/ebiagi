from threading import Timer
from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase
from _utils import catch_exception, color_name
from _Set import Set
from _Socket import Socket

class ActionsBase(UserActionsBase):

    @catch_exception
    def create_actions(self):

        self.tracks = []
        self.set = None
        self.socket = None

        self.add_global_action('rebuild_set', self.rebuild_set)
        self.add_global_action('activate_module', self.activate_module)
        self.add_global_action('select_instrument', self.select_instrument)
        self.add_global_action('deselect_instrument', self.deselect_instrument)
        self.add_global_action('select_input', self.select_input)
        self.add_global_action('deselect_input', self.deselect_input)

        self.socket = Socket(self)
        

    @catch_exception
    def rebuild_set(self, action_def, args):
        self.set = Set(self)

    @catch_exception
    def activate_module(self, action_def, args):
        index = int(args) - 1
        self.set.activate_module(index)

    @catch_exception
    def select_instrument(self, action_def, args):
        index = int(args[-1]) - 1
        self.set.active_module.select_instrument(index)

    @catch_exception
    def deselect_instrument(self, action_def, args):
        index = int(args[-1]) - 1
        self.set.active_module.deselect_instrument(index)

    @catch_exception
    def select_input(self, action_def, args):
        self.set.select_input(args.upper())

    @catch_exception
    def deselect_input(self, action_def, args):
        self.set.deselect_input(args.upper())

    @catch_exception
    def get_state(self):
        if self.set:

            instr = []
            inputs = {}

            for midi_input in self.set.midi_inputs:
                inputs[midi_input] = 'dark'

            for instrument in self.set.active_module.instruments:
                color = color_name(instrument.track.color_index)
                brightness = 0
                for midi_input in self.set.midi_inputs:
                    if instrument.get_input(midi_input) and instrument.get_input(midi_input).arm == 1:
                        brightness = 1
                        if inputs[midi_input] == 'dark':
                            inputs[midi_input] = color
                        else:
                            inputs[midi_input] = 'white'
                instr.append({
                    'index': self.set.active_module.instruments.index(instrument),
                    'color': color, 
                    'brightness': brightness, 
                })

            return {
                'instr': instr,
                'inputs': inputs
            }

        else:
            return 'no active set'

    def log(self, message):
        self.canonical_parent.log_message(message)