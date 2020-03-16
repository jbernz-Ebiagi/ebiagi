from GlobalActions import catch_exception


class CbordActions:

    def __init__(self, GlobalActions):
        self.parent = GlobalActions
        self.parent.add_global_action('arm_cbord_instrument', self.arm_cbord_instrument)
        self.parent.add_global_action('select_cbord', self.select_cbord)


    # Actions ----------------------------------------------------------------------------


    @catch_exception
    def arm_cbord_input(self, action_def, args):
        index = int(args) - 1 
        input = self.parent.cbord_inputs[index]


    @catch_exception
    def select_cbord(self, action_def, args):
        self.parent.log('select')


    # Utils ------------------------------------------------------------------------------
    

    def _update_cbord_inputs(self):
        self.parent.cbord_inputs = []
        for track in self.parent.song().tracks:
            if track.name == 'MIDI_IN':
                for chain in track.device[0].chains:
                    if chain.name == 'CBORD':
                        self.parent.cbord_inputs.append[track]  