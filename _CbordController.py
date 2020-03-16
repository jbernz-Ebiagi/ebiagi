
class CbordController:

    def __init__(self, GlobalActions):
        self.parent = GlobalActions
        self.parent.add_global_action('select_cbord', self.select_cbord)
        
        self.inputs = []
        self.selected_input = None
        self._update_input_list()


    # Actions ----------------------------------------------------------------------------


    def select_cbord(self, action_def, args):
        index = int(args) - 1 
        self.selected_input = self.inputs[index]
        self._update_selection()
        self.parent._update_data()
        self.parent._update_selected_instruments()


    # Utils ------------------------------------------------------------------------------
    

    def _update_input_list(self):
        self.inputs = []
        for track in self.parent.song().tracks:
            if track.name == 'MIDI_IN':
                for chain in track.devices[0].chains:
                    if chain.name == 'CBORD':
                        self.inputs.append(track)
        if len(self.inputs) > 0:
            self.selected_input = self.inputs[0]
        self.parent._update_data()


    def _update_selection(self):
        for input in self.inputs:
            for chain in track.devices[0].chains:
                if chain.name == 'CBORD':
                    if track is self.selected_input:
                        chain.mute = 0
                    else:
                        chain.mute = 1