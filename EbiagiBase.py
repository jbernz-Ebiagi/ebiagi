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
        self.add_global_action('select_instrument', self.select_instrument)
        self.add_global_action('deselect_instrument', self.deselect_instrument)
        self.add_global_action('select_loop', self.select_loop)
        self.add_global_action('deselect_loop', self.deselect_loop)
        self.add_global_action('stop_loop', self.stop_loop)
        self.add_global_action('stop_all_loops', self.stop_all_loops)
        self.add_global_action('clear_loop', self.clear_loop)
        self.add_global_action('toggle_metronome', self.toggle_metronome)

        self.socket = Socket(self)  

    @catch_exception
    def rebuild_set(self, action_def, args):
        self.set = Set()

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
    def select_loop(self, action_def, args):
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
    def stop_all_loops(self, action_def, args):
        self.set.stop_all_loops()

    @catch_exception    
    def toggle_metronome(self, action_def, args):
        self.set.toggle_metronome()

    @catch_exception
    def get_state(self):
        return get_state(self.set)

    def log(self, message):
        self.canonical_parent.log_message(message)