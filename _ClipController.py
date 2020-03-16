class ClipController:

    def __init__(self, GlobalActions):
        self.parent = GlobalActions
        self.parent.add_global_action('select_clip', self.select_clip)
        self.parent.add_global_action('deselect_clip', self.deselect_clip)

        self.held_clips = set([])


    # Actions ----------------------------------------------------------------------------


    def select_clip(self, action_def, args):
        clip_name = args.upper()
        scene = self._get_clip_scene(clip_name)
        scene.fire()
        self._select_clip(scene)


    def deselect_clip(self, action_def, args):
        clip_name = args.upper()
        scene = self._get_clip_scene(clip_name)
        self._deselect_clip(scene)


    # Utils ------------------------------------------------------------------------------

    def _select_clip(self, scene):
        self.held_clips.add(scene)
        self.parent._update_data()
        self.parent._update_selected_instruments()


    def _deselect_clip(self, scene):
        self.held_clips.remove(scene)
        if self.parent._total_held() > 0:
            self.parent._update_data()
            self.parent._update_selected_instruments()    


    def _get_clip_scene(self, scene_name):
        for scene in self.parent.song().scenes:
            if scene_name.upper() in scene.name:
                return scene
        return False

    
    def log(self, msg):
        self.parent.log(msg)