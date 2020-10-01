from threading import Timer
from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase
from _utils import catch_exception, color_name
from _Set import Set
from _Socket import Socket
from _Scheduler import start_scheduler, schedule

class ActionsBase(UserActionsBase):

    @catch_exception
    def create_actions(self):

        self.tracks = []
        self.set = None
        self.socket = None

        self.add_global_action('rebuild_set', self.rebuild_set)
        self.add_global_action('activate_module', self.activate_module)

        self.socket = Socket(self)

        start_scheduler()
        

    @catch_exception
    def rebuild_set(self, action_def, args):
        self.log('wee')
        self.set = Set(self)

    @catch_exception
    def activate_module(self, action_def, args):
        index = int(args[-1]) - 1
        self.set.activate_module(index)

    @catch_exception
    def get_state(self):
        if self.set:


            modules = []
            loops = []
            
            mfx = []
            gfx = []
            global_loops = []
            instr = []
            inputs = {}

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

            for key in self.set.loops:
                loop = self.set.loops[key]
                color = 'red'
                instrument = loop.instrument
                if not loop.is_recording() and loop.instrument:
                    color = color_name(loop.instrument.track.color_index)
                brightness = 0
                if loop.is_playing():
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
                'mfx': mfx,
                'gfx': gfx,
                'globalLoops': global_loops
            }

        else:
            return 'no active set'

    def log(self, message):
        self.canonical_parent.log_message(message)