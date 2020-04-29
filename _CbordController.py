from _utils import catch_exception
from threading import Timer

class CbordController:

    def __init__(self, GlobalActions):
        self.parent = GlobalActions
        self.parent.add_global_action('select_cbord', self.select_cbord)
        self.parent.add_global_action('reset_cbord_params', self.reset_cbord_params)
        
        self.inputs = []
        self.selected_input = None

        Timer(0.5, self._update_input_list).start()


    # Actions ----------------------------------------------------------------------------

    
    @catch_exception
    def select_cbord(self, action_def, args):
        index = int(args[-1]) - 1
        self.log(index)
        self.selected_input = self.inputs[index]
        self.parent._select_instrument(self.selected_input)


    @catch_exception
    def reset_cbord_params(self, action_def, args):
        index = int(args[-1]) - 1 
        group = self.parent._get_parent(self.parent._get_parent(self.inputs[index]))
        instr = self.parent._get_child_with_name(group, 'INSTR')
        for i in range(1,9):
            instr.devices[0].parameters[i].value = self.parent.saved_params[group.name + '_' + instr.name][i]



    # Utils ------------------------------------------------------------------------------
    

    def _update_input_list(self):
        self.inputs = []
        for track in self.parent.song().tracks:
            self.log(track.name)
            self.log(track.input_routing_type.display_name)
            if track.name == 'CTRL_IN' and track.input_routing_type.display_name == 'ALL_IN':
                self.log('append input')
                self.inputs.append(track)
        if len(self.inputs) > 0:
            self.selected_input = self.inputs[0]


    def log(self, msg):
        self.parent.log(msg)