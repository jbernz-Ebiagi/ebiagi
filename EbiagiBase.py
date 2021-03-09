from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase
from _utils import catch_exception, clear_log_file
from _Set import Set
from _Socket import Socket
from _GetState import get_state

#This file is the entry point to the control surface script, and defines/routes the available actions
class EbiagiBase(UserActionsBase):

    @catch_exception    
    def __init__(self, *a, **k):
        super(EbiagiBase, self).__init__(*a, **k)
        self.socket = None
        self.set = None

    @catch_exception
    def create_actions(self):

        clear_log_file()
        self.log('initializing Ebiagi...')

        self.add_global_action('rebuild_set', self.rebuild_set)
        self.add_global_action('activate_module', self.activate_module)
        self.add_global_action('toggle_input', self.toggle_input)
        self.add_global_action('select_instrument', self.select_instrument)
        self.add_global_action('deselect_instrument', self.deselect_instrument)
        self.add_global_action('stop_instrument', self.stop_instrument)
        self.add_global_action('select_loop', self.select_loop)
        self.add_global_action('deselect_loop', self.deselect_loop)
        self.add_global_action('stop_loop', self.stop_loop)
        self.add_global_action('stop_all_loops', self.stop_all_loops)
        self.add_global_action('clear_loop', self.clear_loop)
        self.add_global_action('mute_all_loops', self.mute_all_loops)
        self.add_global_action('unmute_all_loops', self.unmute_all_loops)
        self.add_global_action('quantize_loop', self.quantize_loop)
        self.add_global_action('select_snap', self.select_snap)
        self.add_global_action('deselect_snap', self.deselect_snap)
        self.add_global_action('assign_snap', self.assign_snap)
        self.add_global_action('clear_snap', self.clear_snap)
        self.add_global_action('recall_snap', self.recall_snap)
        self.add_global_action('select_global_instrument', self.select_global_instrument)
        self.add_global_action('deselect_global_instrument', self.deselect_global_instrument)
        self.add_global_action('select_global_loop', self.select_global_loop)
        self.add_global_action('stop_global_loop', self.stop_global_loop)
        self.add_global_action('clear_global_loop', self.clear_global_loop)
        self.add_global_action('toggle_metronome', self.toggle_metronome)
        self.add_global_action('smart_record', self.smart_record)
        self.add_global_action('smart_clear', self.smart_clear)

        self.socket = Socket(self)  

    @catch_exception
    def rebuild_set(self, action_def, args):
        self.set = Set()

    @catch_exception
    def activate_module(self, action_def, args):
        index = int(args[-1])
        self.set.activate_module(index)

    @catch_exception
    def toggle_input(self, action_def, args):
        self.set.toggle_input(args.upper())

    @catch_exception
    def select_instrument(self, action_def, args):
        index = int(args[-1])
        self.set.select_instrument(index)

    @catch_exception
    def deselect_instrument(self, action_def, args):
        index = int(args[-1])
        self.set.deselect_instrument(index)

    @catch_exception
    def stop_instrument(self, action_def, args):
        index = int(args[-1])
        self.set.stop_instrument(index)

    @catch_exception    
    def select_loop(self, action_def, args):
        self.log(args)
        self.set.select_loop(args)

    @catch_exception    
    def deselect_loop(self, action_def, args):
        self.set.deselect_loop(args)

    @catch_exception    
    def stop_loop(self, action_def, args):
        self.set.stop_loop(args)
        
    @catch_exception    
    def clear_loop(self, action_def, args):
        self.set.clear_loop(args)

    @catch_exception    
    def quantize_loop(self, action_def, args):
        self.set.quantize_loop(args)

    @catch_exception    
    def mute_all_loops(self, action_def, args):
        self.set.mute_all_loops()

    @catch_exception    
    def unmute_all_loops(self, action_def, args):
        self.set.unmute_all_loops()

    @catch_exception    
    def stop_all_loops(self, action_def, args):
        self.set.stop_all_loops()

    @catch_exception    
    def select_snap(self, action_def, args):
        index = int(args[-1])
        self.set.select_snap(index)

    @catch_exception    
    def deselect_snap(self, action_def, args):
        index = int(args[-1])
        self.set.deselect_snap(index)

    @catch_exception    
    def assign_snap(self, action_def, args):
        index = int(args[-1])
        self.set.assign_snap(index)

    @catch_exception    
    def clear_snap(self, action_def, args):
        index = int(args[-1]) 
        self.set.clear_snap(index)

    @catch_exception    
    def recall_snap(self, action_def, args):
        beats = 0
        if args:
            beats = int(args)*4
        self.set.recall_snap(beats)

    @catch_exception
    def select_global_instrument(self, action_def, args):
        index = int(args[-1])
        self.set.select_global_instrument(index)

    @catch_exception
    def deselect_global_instrument(self, action_def, args):
        index = int(args[-1])
        self.set.deselect_global_instrument(index)

    @catch_exception    
    def select_global_loop(self, action_def, args):
        self.set.select_global_loop()

    @catch_exception    
    def stop_global_loop(self, action_def, args):
        self.set.stop_global_loop()

    @catch_exception    
    def clear_global_loop(self, action_def, args):
        self.set.clear_global_loop()

    @catch_exception    
    def toggle_metronome(self, action_def, args):
        self.set.toggle_metronome()

    @catch_exception    
    def smart_record(self, action_def, args):
        self.set.smart_record()

    @catch_exception    
    def smart_clear(self, action_def, args):
        self.set.smart_clear()

    @catch_exception
    def get_state(self):
        return get_state(self.set)

    def log(self, message):
        self.canonical_parent.log_message(message)