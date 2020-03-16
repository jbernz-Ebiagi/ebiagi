class ClipActions:

    def __init__(self, GlobalActions):
        self.parent = GlobalActions
        self.parent.add_global_action('select_clip', self.select_clip)
        self.parent.add_global_action('deselect_clip', self.deselect_clip)


    # Actions ----------------------------------------------------------------------------


    def select_clip(self, action_def, args):
        clip_name = args.upper()
        scene = self.parent._get_clip_scene(clip_name)
        self.parent._trigger_scene(scene)
        self.parent._select_scene(scene)


    def deselect_clip(self, action_def, args):
        clip_name = args.upper()
        scene = self._get_clip_scene(clip_name)
        self.parent._deselect_scene(scene)


    # Utils ------------------------------------------------------------------------------


    def _get_clip_scene(self, scene_name):
        for scene in self.song().scenes:
            if scene_name.upper() in scene.name:
                return scene
        return False