class FXActions:

    def __init__(self, GlobalActions):
        self.parent = GlobalActions
        self.parent.add_global_action('select_fx', self.select_fx)
        self.parent.add_global_action('deselect_fx', self.deselect_fx)
        self.parent.add_global_action('reset_fx_params', self.reset_fx_params)
        self.parent.add_global_action('reset_all_fx_params', self.reset_all_fx_params)


    # Actions ----------------------------------------------------------------------------


    def select_fx(self, action_def, args):
        fx_name = args.upper()
        device = self._get_fx_device(fx_name)
        self._select_fx_device(device)


    def deselect_fx(self, action_def, args):
        fx_name = args.upper()
        device = self._get_fx_device(fx_name)
        self._deselect_fx_device(device)


    def reset_fx_params(self, action_def, args):
        fx_name = args.upper()
        device = self._get_fx_device(fx_name)
        self._reset_fx_params(device)


    def reset_all_fx_params(self, action_def, args):
        for track in self.parent.song().tracks:
            if track.name == 'FX':
                for device in track.devices:
                    self._reset_fx_params(device)


    # Utils ------------------------------------------------------------------------------
    

    def _get_fx_device(self, device_name):
        for track in self.parent.song().tracks:
            if track.name == 'FX':
                for device in track.devices:
                    if device.name == device_name:
                        return device
        return False


    def _select_fx_device(self, device):
        self.parent.held_fx.add(device)
        self.parent._update_data()
        self.parent._update_selected_instruments()


    def _deselect_fx_device(self, device):
        self.parent.held_fx.remove(device)
        if len(self.parent.held_scenes) + len(self.parent.held_fx) > 0:
            self.parent._update_data()
            self.parent._update_selected_instruments()       


    def _reset_fx_params(self, device):
        for i in range(1,9):
            device.parameters[i].value = self.parent.saved_params[device.name][i]   