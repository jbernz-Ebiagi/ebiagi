from _utils import catch_exception

class GlobalFXController:

    def __init__(self, GlobalActions):
        self.parent = GlobalActions
        self.parent.add_global_action('select_fx', self.select_fx)
        self.parent.add_global_action('deselect_fx', self.deselect_fx)
        self.parent.add_global_action('reset_fx_params', self.reset_fx_params)
        self.parent.add_global_action('reset_all_fx_params', self.reset_all_fx_params)


    # Actions ----------------------------------------------------------------------------

    @catch_exception
    def select_fx(self, action_def, args):
        fx_index = int(args[-1]) - 1 
        track = self._get_fx_track(fx_index)
        self._select_fx_track(track)


    @catch_exception
    def deselect_fx(self, action_def, args):
        fx_index = int(args[-1]) - 1
        track = self._get_fx_track(fx_index)
        self._deselect_fx_track(track)


    def reset_fx_params(self, action_def, args):
        fx_index = int(args[-1]) - 1
        track = self._get_fx_track(fx_index)
        self._reset_fx_params(track)


    def reset_all_fx_params(self, action_def, args):
        for track in self.parent.song().tracks:
            if 'GFX' in track.name:
                self._reset_fx_params(track)


    # Utils ------------------------------------------------------------------------------
    

    def _get_fx_track(self, fx_index):
        for track in self.parent.song().tracks:
            if track.name == 'GLOBAL_FX':
                children = self.parent._get_children(track)
                return children[fx_index]
        return False


    def _select_fx_track(self, track):
        self.parent._select_fx(track)


    def _deselect_fx_track(self, track):
        self.parent._deselect_fx(track)  


    def _reset_fx_params(self, track):
        device = track.devices[0]
        for i in range(1,9):
            device.parameters[i].value = self.parent.saved_params['GLOBAL_FX_' + track.name][i]   


    def log(self, msg):
        self.parent.log(msg)