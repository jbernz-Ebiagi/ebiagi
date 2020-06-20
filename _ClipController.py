from _utils import catch_exception
from threading import Timer

class ClipController:

    def __init__(self, GlobalActions):
        self.parent = GlobalActions
        self.parent.add_global_action('select_clip', self.select_clip)
        self.parent.add_global_action('deselect_clip', self.deselect_clip)
        self.parent.add_global_action('choke', self.choke)
        self.parent.add_global_action('unchoke', self.unchoke)


    # Actions ----------------------------------------------------------------------------

    @catch_exception
    def select_clip(self, action_def, args):
        clip_name = args.upper()
        scene = self._get_clip_scene(clip_name)
        self._select_clip(scene)


    @catch_exception
    def deselect_clip(self, action_def, args):
        clip_name = args.upper()
        scene = self._get_clip_scene(clip_name)
        self._deselect_clip(scene)


    @catch_exception
    def choke(self, action_def, args):
        track_name = args.upper()
        instr_group = self.parent._get_track_with_name(track_name)
        self.parent.loop._mute_loops_by_instr(instr_group)


    @catch_exception
    def unchoke(self, action_def, args):
        track_name = args.upper()
        instr_group = self.parent._get_track_with_name(track_name)
        self.parent.loop._unmute_loops_by_instr(instr_group)


    # Utils ------------------------------------------------------------------------------

    def _select_clip(self, scene):
        clip_tracks = self.parent._get_tracks_of_scene(scene)
        if len(clip_tracks) > 0:
            clip_group = self.parent._get_parent(clip_tracks[0])
            instr_group = self.parent._get_parent(clip_group)

            self.parent.song().view.selected_scene = scene

            scene.fire()

            for clip_slot in scene.clip_slots:
                if clip_slot.has_clip and 'CHOKE' in clip_slot.clip.name:
                    self.parent.loop._mute_loops_by_instr(instr_group)
                if clip_slot.has_clip and 'SELECT' in clip_slot.clip.name:
                    as_in = self.parent._get_child_with_name(self.parent._get_child_with_name(instr_group, 'ROUTING'), 'AS_IN')
                    self.parent._assign_as(as_in)
                    self.parent._deselect_as(as_in)
  

    def _deselect_clip(self, scene):
        self.log(scene.name)
        clip_tracks = self.parent._get_tracks_of_scene(scene)
        if len(clip_tracks) > 0:
            clip_group = self.parent._get_parent(clip_tracks[0])
            instr_group = self.parent._get_parent(clip_group)

            for clip_slot in scene.clip_slots:
                if clip_slot.has_clip and 'CHOKE' in clip_slot.clip.name and not 'unchoke' in clip_slot.clip.name:
                    self.parent.loop._unmute_loops_by_instr(instr_group)
                if clip_slot.has_clip and 'GATE' in clip_slot.clip.name:
                    clip_slot.stop()
                    if 'GATE:' in clip_slot.clip.name:
                        self._get_clip_scene(clip_slot.clip.name.split('GATE:',1)[1]).set_fire_button_state(1)


    def _get_clip_scene(self, scene_name):
        for scene in self.parent.song().scenes:
            if scene_name.upper() in scene.name:
                return scene
        return False

    
    def log(self, msg):
        self.parent.log(msg)