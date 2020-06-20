from _utils import catch_exception

class GlobalFXController:

    def __init__(self, GlobalActions):
        self.parent = GlobalActions
        self.parent.add_global_action('select_fx', self.select_fx)
        self.parent.add_global_action('deselect_fx', self.deselect_fx)


    # Actions ----------------------------------------------------------------------------

    @catch_exception
    def select_fx(self, action_def, args):
        fx_index = int(args[-1]) - 1 
        track = self._get_fx_track(fx_index)
        self._select_fx_track(track)
        self.parent.show_audio_swift()


    @catch_exception
    def deselect_fx(self, action_def, args):
        fx_index = int(args[-1]) - 1
        track = self._get_fx_track(fx_index)
        self._deselect_fx_track(track)


    # Utils ------------------------------------------------------------------------------
    

    def _get_fx_track(self, fx_index):
        for track in self.parent.song().tracks:
            if track.name == 'GLOBAL_FX':
                children = self.parent._get_children(track)
                return children[fx_index]
        return False


    def _select_fx_track(self, track):
        self.parent._assign_as(track)


    def _deselect_fx_track(self, track):
        self.parent._deselect_as(track)  


    def log(self, msg):
        self.parent.log(msg)