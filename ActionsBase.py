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
        self.add_global_action('select_instrument', self.select_instrument)
        self.add_global_action('deselect_instrument', self.deselect_instrument)
        self.add_global_action('stop_instrument', self.stop_instrument)
        self.add_global_action('select_loop', self.select_loop)
        self.add_global_action('stop_loop', self.stop_loop)
        self.add_global_action('stop_all_loops', self.stop_all_loops)
        self.add_global_action('clear_loop', self.clear_loop)
        self.add_global_action('play_clip', self.play_clip)
        self.add_global_action('stop_clip', self.stop_clip)
        self.add_global_action('select_mfx', self.select_mfx)
        self.add_global_action('deselect_mfx', self.deselect_mfx)
        self.add_global_action('select_gfx', self.select_gfx)
        self.add_global_action('deselect_gfx', self.deselect_gfx)
        self.add_global_action('select_global_loop', self.select_global_loop)
        self.add_global_action('stop_global_loop', self.stop_global_loop)
        self.add_global_action('clear_global_loop', self.clear_global_loop)
        self.add_global_action('toggle_input', self.toggle_input)
        self.add_global_action('mute_all_loops', self.mute_all_loops)
        self.add_global_action('unmute_all_loops', self.unmute_all_loops)
        self.add_global_action('recall_snap', self.recall_snap)
        self.add_global_action('select_snap', self.select_snap)
        self.add_global_action('deselect_snap', self.deselect_snap)
        self.add_global_action('assign_snap', self.assign_snap)
        self.add_global_action('clear_snap', self.clear_snap)

        self.socket = Socket(self)

        self.log(self.value_ramper)

        

    @catch_exception
    def rebuild_set(self, action_def, args):
        self.log('wee')
        self.set = Set(self)

    @catch_exception
    def activate_module(self, action_def, args):
        index = int(args[-1]) - 1
        self.set.activate_module(index)

    @catch_exception
    def select_instrument(self, action_def, args):
        index = int(args[-1]) - 1
        self.set.select_instrument(index)

    @catch_exception
    def deselect_instrument(self, action_def, args):
        index = int(args[-1]) - 1
        self.set.deselect_instrument(index)

    @catch_exception
    def stop_instrument(self, action_def, args):
        index = int(args[-1]) - 1
        self.set.stop_instrument(index)

    @catch_exception
    def select_mfx(self, action_def, args):
        index = int(args[-1]) - 1
        self.set.select_mfx(index)

    @catch_exception
    def deselect_mfx(self, action_def, args):
        index = int(args[-1]) - 1
        self.set.deselect_mfx(index)

    @catch_exception    
    def select_loop(self, action_def, args):
        self.set.select_loop(args)

    @catch_exception    
    def stop_loop(self, action_def, args):
        self.set.stop_loop(args)
        
    @catch_exception    
    def clear_loop(self, action_def, args):
        self.set.clear_loop(args)

    @catch_exception    
    def stop_loop(self, action_def, args):
        self.set.stop_loop(args)

    @catch_exception    
    def stop_all_loops(self, action_def, args):
        self.set.stop_all_loops()

    @catch_exception    
    def play_clip(self, action_def, args):
        self.set.play_clip(args.upper())

    @catch_exception    
    def stop_clip(self, action_def, args):
        self.set.stop_clip(args.upper())

    @catch_exception
    def select_gfx(self, action_def, args):
        index = int(args[-1]) - 1
        self.set.select_gfx(index)

    @catch_exception
    def deselect_gfx(self, action_def, args):
        index = int(args[-1]) - 1
        self.set.deselect_gfx(index)

    @catch_exception    
    def select_global_loop(self, action_def, args):
        index = int(args[-1]) - 1
        self.set.select_global_loop(index)

    @catch_exception    
    def stop_global_loop(self, action_def, args):
        index = int(args[-1]) - 1
        self.set.stop_global_loop(index)

    @catch_exception    
    def clear_global_loop(self, action_def, args):
        index = int(args[-1]) - 1
        self.set.clear_global_loop(index)

    @catch_exception
    def toggle_input(self, action_def, args):
        self.set.toggle_input(args.upper())

    @catch_exception    
    def mute_all_loops(self, action_def, args):
        self.set.active_module.mute_all_loops()

    @catch_exception    
    def unmute_all_loops(self, action_def, args):
        self.set.active_module.unmute_all_loops()

    @catch_exception    
    def recall_snap(self, action_def, args):
        beats = 0
        if args:
            beats = 4*2**(int(args[-1]) - 1)
        self.set.recall_snap(beats)

    @catch_exception    
    def select_snap(self, action_def, args):
        index = int(args[-1]) - 1
        self.set.select_snap(index)

    @catch_exception    
    def deselect_snap(self, action_def, args):
        index = int(args[-1]) - 1
        self.set.deselect_snap(index)

    @catch_exception    
    def assign_snap(self, action_def, args):
        index = int(args[-1]) - 1
        self.set.assign_snap(index)

    @catch_exception    
    def clear_snap(self, action_def, args):
        index = int(args[-1]) - 1
        self.set.clear_snap(index)

    @catch_exception
    def get_state(self):
        if self.set and not self.set.loading:

            modules = []
            loops = []
            clips = []
            instr = []
            inputs = {}

            mfx = []
            gfx = []
            global_loops = []
            snaps = []

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
                if not loop.is_recording() and loop.instrument and loop.has_clip():
                    color = color_name(loop.instrument.track.color_index)
                brightness = 0
                if loop.is_playing():
                    brightness = 1
                loops.append({
                    'key_name': key,
                    'color': color, 
                    'brightness': brightness,
                })

            for key in self.set.clips:
                clip = self.set.clips[key]
                instrument = clip.instrument
                if clip.instrument and clip.has_clip():
                    color = color_name(clip.instrument.track.color_index)
                else:
                    color = 'dark'
                brightness = 0
                if clip.is_playing():
                    brightness = 1
                clips.append({
                    'clip_name': key,
                    'color': color, 
                    'brightness': brightness,
                })

            #
            for inpt in self.set.inputs:    
                ipt = self.set.inputs[inpt]            
                instrs = ipt.get_armed_instruments()
                if len(instrs) > 1:
                    inputs[ipt.short_name] = 'white'
                elif len(instrs) == 1:
                    inputs[ipt.short_name] = color_name(instrs[0].track.color_index)
                else:
                    inputs[ipt.short_name] = 'dark'
                if ipt.track.mute == 1:
                    inputs[ipt.short_name] = 'dark'


            for instrument in self.set.active_module.main_instruments:
                color = color_name(instrument.track.color_index)
                brightness = 0
                for name in instrument.input_names:
                    if instrument.router.input_is_armed(name):
                        brightness = 1
                instr.append({
                    'index': self.set.active_module.main_instruments.index(instrument),
                    'color': color, 
                    'brightness': brightness,
                })

            for module_fx in self.set.active_module.mfx_instruments:
                brightness = 0
                for name in module_fx.input_names:
                    if module_fx.router.input_is_armed(name):
                        brightness = 1
                mfx.append({
                    'index': self.set.active_module.mfx_instruments.index(module_fx),
                    'color': 'white', 
                    'brightness': brightness, 
                })

            for global_fx in self.set.global_fx:
                brightness = 0
                if global_fx.arm == 1:
                    brightness = 1
                    inputs['AS'] = 'white'
                gfx.append({
                    'index': self.set.global_fx.index(global_fx),
                    'color': 'white', 
                    'brightness': brightness, 
                })

            for global_loop in self.set.global_loops:
                color = 'red' if global_loop.is_recording else 'white'
                brightness = 1 if global_loop.is_playing else 0
                global_loops.append({
                    'index': self.set.global_loops.index(global_loop),
                    'color': color, 
                    'brightness': brightness,
                })

            for snap in self.set.active_module.snaps:
                color = 'blue' if snap is self.set.snap_fx.selected_snap else 'white'
                brightness = 1 if len(snap) > 0 else 0
                snaps.append({
                    'index': self.set.active_module.snaps.index(snap),
                    'color': color, 
                    'brightness': brightness,
                })

            return {
                'instr': instr,
                'inputs': inputs,
                'modules': modules,
                'loops': loops,
                'clips': clips,
                'mfx': mfx,
                'gfx': gfx,
                'globalLoops': global_loops,
                'snaps': snaps
            }

        else:
            return 'no active set'

    def log(self, message):
        self.canonical_parent.log_message(message)