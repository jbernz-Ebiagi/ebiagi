from _utils import catch_exception

class EnvClipController:

    def __init__(self, GlobalActions):
        self.parent = GlobalActions
        self.parent.add_global_action('select_env_clip', self.select_env_clip)


    # Actions ----------------------------------------------------------------------------

    @catch_exception
    def select_env_clip(self, action_def, args):
        clip_name = args.upper()
        scene = self._get_clip_scene(clip_name)
        self._select_env_clip(scene)


    # Utils ------------------------------------------------------------------------------

    def _select_env_clip(self, scene):
        clip_tracks = self.parent._get_tracks_of_scene(scene)
        sceneIndex = list(self.parent.song().scenes).index(scene)
        for track in clip_tracks:
            if 'GFX' in track.name and track in self.parent.selected_as_fx:
                track.clip_slots[sceneIndex].fire()
            else:
                clip_group = self.parent._get_parent(track)
                instr_group = self.parent._get_parent(clip_group)
                routing_group = self.parent._get_child_with_name(instr_group, 'ROUTING')
                as_track = self.parent._get_child_with_name(routing_group, 'AS_IN')
                if as_track in self.parent.selected_as_fx:
                    instr_group.clip_slots[sceneIndex].fire()


    def _get_clip_scene(self, scene_name):
        for scene in self.parent.song().scenes:
            if scene_name.upper() in scene.name:
                return scene
        return False

    
    def log(self, msg):
        self.parent.log(msg)