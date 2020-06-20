from _utils import catch_exception
from threading import Timer

class CbordController:

    def __init__(self, GlobalActions):
        self.parent = GlobalActions
        self.parent.add_global_action('select_cbord', self.select_cbord)
        self.parent.add_global_action('release_select_cbord', self.release_select_cbord)
        
        self.inputs = []
        self.selected_input = None

        Timer(0.5, self._update_input_list).start()


    # Actions ----------------------------------------------------------------------------

    
    @catch_exception
    def select_cbord(self, action_def, args):
        index = int(args[-1]) - 1
        self.selected_input = self.inputs[index]
        self.parent._assign_cbord(self.selected_input)
        self.parent.show_audio_swift()


    @catch_exception
    def release_select_cbord(self, action_def, args):
        index = int(args[-1]) - 1
        selected_input = self.inputs[index]
        routing_group = self.parent._get_parent(selected_input)
        as_in = self.parent._get_child_with_name(routing_group, 'AS_IN')
        self.parent.selected_as_fx.remove(as_in)


    # Utils ------------------------------------------------------------------------------
    

    def _update_input_list(self):
        self.inputs = []
        for track in self.parent.song().tracks:
            if track.name == 'CBORD_IN':
                self.inputs.append(track)
        if len(self.inputs) > 0:
            self.selected_input = self.inputs[0]


    def log(self, msg):
        self.parent.log(msg)