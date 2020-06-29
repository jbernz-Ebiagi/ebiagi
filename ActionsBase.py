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
        self.add_global_action('select_mfx', self.select_mfx)
        self.add_global_action('deselect_mfx', self.deselect_mfx)
        self.add_global_action('select_input', self.select_input)
        self.add_global_action('deselect_input', self.deselect_input)
        self.add_global_action('select_loop', self.select_loop)
        self.add_global_action('deselect_loop', self.deselect_loop)
        self.add_global_action('stop_loop', self.stop_loop)
        self.add_global_action('stop_all_loops', self.stop_all_loops)
        self.add_global_action('clear_loop', self.clear_loop)
        self.add_global_action('clear_module', self.clear_module)
        self.add_global_action('toggle_input', self.toggle_input)

        self.socket = Socket(self)
        

    @catch_exception
    def rebuild_set(self, action_def, args):
        self.set = Set(self)

    @catch_exception
    def activate_module(self, action_def, args):
        index = int(args[-1]) - 1
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
    def select_mfx(self, action_def, args):
        index = int(args[-1]) - 1
        self.set.active_module.select_mfx(index)

    @catch_exception
    def deselect_mfx(self, action_def, args):
        index = int(args[-1]) - 1
        self.set.active_module.deselect_mfx(index)

    @catch_exception
    def select_input(self, action_def, args):
        self.set.select_input(args.upper())

    @catch_exception
    def deselect_input(self, action_def, args):
        self.set.deselect_input(args.upper())

    @catch_exception
    def toggle_input(self, action_def, args):
        self.set.toggle_input(args.upper())

    @catch_exception    
    def select_loop(self, action_def, args):
        self.set.active_module.select_loop(args)

    @catch_exception
    def deselect_loop(self, action_def, args):
        self.set.active_module.deselect_loop(args)

    @catch_exception    
    def stop_loop(self, action_def, args):
        self.set.active_module.stop_loop(args)

    @catch_exception    
    def stop_all_loops(self, action_def, args):
        self.set.active_module.stop_all_loops()

    @catch_exception    
    def clear_loop(self, action_def, args):
        self.set.active_module.clear_loop(args)

    @catch_exception
    def clear_module(self, action_def, args):
        index = int(args[-1]) - 1
        self.set.clear_module(index)

    @catch_exception
    def get_state(self):
        if self.set:

            instr = []
            inputs = {}
            modules = []
            loops = []
            mfx = []

            for inpt in self.set.midi_inputs + self.set.audio_inputs:
                inputs[inpt] = 'dark'

            for instrument in self.set.active_module.instruments:
                color = color_name(instrument.track.color_index)
                brightness = 0
                for inpt in self.set.midi_inputs + self.set.audio_inputs:
                    if instrument.get_input(inpt) and instrument.get_input(inpt).arm == 1:
                        brightness = 1
                        if inputs[inpt] == 'dark':
                            inputs[inpt] = color
                        else:
                            inputs[inpt] = 'white'
                instr.append({
                    'index': self.set.active_module.instruments.index(instrument),
                    'color': color, 
                    'brightness': brightness, 
                })

            for module_fx in self.set.active_module.module_fx:
                brightness = 0
                if module_fx.track.arm == 1:
                    brightness = 1
                mfx.append({
                    'index': self.set.active_module.module_fx.index(module_fx),
                    'color': 'white', 
                    'brightness': brightness, 
                })

            for module in self.set.modules:
                color = color_name(module.track.color_index)
                brightness = 0
                if module is self.set.active_module:
                    brightness = 1
                modules.append({
                    'index': self.set.modules.index(module),
                    'color': color, 
                    'brightness': brightness,
                }) 

            for key in self.set.active_module.loops:
                loop = self.set.active_module.loops[key]
                color = 'red'
                instruments = loop.get_instruments()
                if not loop.main_clip_slot.is_recording:
                    if len(instruments) > 1 or len(loop.get_mfx()) > 0:
                        color = 'white'
                    elif len(instruments) == 1:
                        color = color_name(instruments.pop().track.color_index)
                brightness = 0
                if loop.main_clip_slot.is_playing:
                    brightness = 1
                loops.append({
                    'key_name': key,
                    'color': color, 
                    'brightness': brightness,
                }) 

            return {
                'instr': instr,
                'inputs': inputs,
                'modules': modules,
                'loops': loops,
                'mfx': mfx
            }

        else:
            return 'no active set'

    def log(self, message):
        self.canonical_parent.log_message(message)