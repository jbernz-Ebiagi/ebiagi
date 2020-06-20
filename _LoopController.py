from _utils import catch_exception

class LoopController:

    def __init__(self, GlobalActions):
        self.parent = GlobalActions
        self.parent.add_global_action('select_loop', self.select_loop)
        self.parent.add_global_action('select_loop_as', self.select_loop_as)
        self.parent.add_global_action('deselect_loop', self.deselect_loop)
        self.parent.add_global_action('clear_loop', self.clear_loop)
        #self.parent.add_global_action('clear_all_loops', self.clear_all_loops)
        self.parent.add_global_action('stop_loop', self.stop_loop)
        self.parent.add_global_action('stop_all_loops', self.stop_all_loops)
        self.parent.add_global_action('stop_all_loops_except_selected', self.stop_all_loops_except_selected)
        self.parent.add_global_action('mute_loop', self.mute_loop)
        self.parent.add_global_action('unmute_loop', self.unmute_loop)
        self.parent.add_global_action('mute_all_loops', self.mute_all_loops)
        self.parent.add_global_action('unmute_all_loops', self.unmute_all_loops)

        self.held_loops = set([])


    # Actions ----------------------------------------------------------------------------

    @catch_exception
    def select_loop(self, action_def, args):
        key_name = args
        scene = self._get_loop_scene(key_name)
        if(scene is not None):
            self.parent.song().view.selected_scene = scene
            #if empty, create a loop
            if(scene.name == 'loop[]'):
                self._create_loop(scene, key_name)
            else:
                for clip_slot in scene.clip_slots:
                    #if recording, finish the record
                    if clip_slot.has_clip and clip_slot.is_recording:
                        self._finish_record(scene)
                        return
                    #if playing, select the loop
                    if clip_slot.has_clip and clip_slot.is_playing and not 'CLIP' in clip_slot.clip.name:
                        self._select_loop(scene)
                        #self.parent.show_audio_swift()
                        return
                #if stopped, fire the loop
                self.parent._trigger_scene(scene)
        else:
            self.parent.log('exceeded maximum loop count')


    @catch_exception
    def select_loop_as(self, action_def, args):
        key_name = args
        scene = self._get_loop_scene(key_name)
        if(scene is not None):
            self._select_loop(scene)
            #self.parent.show_audio_swift()


    @catch_exception
    def deselect_loop(self, action_def, args):
        key_name = args
        scene = self._get_loop_scene(key_name)
        if(scene is not None):
            self._deselect_loop(scene)


    @catch_exception    
    def clear_loop(self, action_def, args):
        key_name = args
        scene = self._get_loop_scene(key_name)
        if(scene and scene.name != 'loop[]' and not 'nd_' in scene.name):
            self._clear_loop(scene)

    @catch_exception
    def stop_loop(self, action_def, args):
        key_name = args
        scene = self._get_loop_scene(key_name)
        if(scene and scene.name != 'loop[]'):
            self._stop_loop(scene)

    @catch_exception
    def stop_all_loops(self, action_def, args):
        scenes = self._get_all_loops()
        for scene in scenes:
            self._stop_loop(scene)

    @catch_exception
    def stop_all_loops_except_selected(self, action_def, args):
        scenes = self._get_all_loops()
        for scene in scenes:
            if not scene in self.held_loops:
                self._stop_loop(scene)

    @catch_exception
    def mute_loop(self, action_def, args):
        key_name = args
        scene = self._get_loop_scene(key_name)
        if(scene and scene.name != 'loop[]'):
            self._mute_loop(scene)

    @catch_exception
    def unmute_loop(self, action_def, args):
        key_name = args
        scene = self._get_loop_scene(key_name)
        if(scene and scene.name != 'loop[]'):
            self._unmute_loop(scene)

    @catch_exception
    def mute_all_loops(self, action_def, args):
        scenes = self._get_all_loops()
        for scene in scenes:
            self._mute_loop(scene) 

    @catch_exception
    def unmute_all_loops(self, action_def, args):
        scenes = self._get_all_loops()
        for scene in scenes:
            self._unmute_loop(scene) 


    # Utils ------------------------------------------------------------------------------


    def _select_loop(self, scene):
        self.held_loops.add(scene)
        as_track = self._get_loop_as_track(scene)
        if as_track:
            self.parent._assign_as(as_track)
            

    def _deselect_loop(self, scene):
        if scene in self.held_loops:
            self.held_loops.remove(scene)
            as_track = self._get_loop_as_track(scene)
            #if another key is selecting the same fx, return
            for s in self.held_loops:
                if self._get_loop_as_track(s) is as_track:
                    return
            self.parent._deselect_as(as_track)


    def _get_loop_as_track(self, scene):
        loop_tracks = self.parent._get_tracks_of_scene(scene)
        loop_group = self.parent._get_parent(loop_tracks[0])
        instr_group = self.parent._get_parent(loop_group)
        routing_group = self.parent._get_child_with_name(instr_group, 'ROUTING')
        return self.parent._get_child_with_name(routing_group, 'AS_IN')


    def _get_loop_scene(self, key_name):
        loop_name = 'loop[' + key_name + ']'
        for scene in self.parent.song().scenes:
            if loop_name in scene.name:
                return scene
        for scene in self.parent.song().scenes:
            if scene.name == 'loop[]':
                return scene
        return False

    
    def _create_loop(self, scene, key_name):
        scene.name = 'loop[' + key_name + ']'
        scene.fire()


    def _get_all_loops(self):
        loops = []
        for scene in self.parent.song().scenes:
            if 'loop' in scene.name and scene.name != 'loop[]':
                loops.append(scene)
        return loops

    
    def _finish_record(self, scene):
        clip_count = 0
        current_group_index = 0
        i = 0
        multi = False
        selected_track = self.parent.song().view.selected_track

        for clip_slot in scene.clip_slots:

            if 'LOOPS' in self.parent.song().tracks[i].name:
                current_group_index = i
                multi = 'MULTI' in self.parent.song().tracks[i].name

            if clip_slot.has_clip:
                self.log(clip_slot.clip.has_envelopes)
                if self.parent._clip_slot_has_notes(clip_slot) or clip_slot.clip.has_envelopes:
                    clip_count += 1
                    n = current_group_index + 1
                    while self.parent.song().tracks[n].name == 'LOOP' and not multi:
                        if not scene.clip_slots[n].has_clip:
                            scene.clip_slots[n].create_clip(1)
                            scene.clip_slots[n].clip.name = "-"
                            scene.clip_slots[n].clip.muted = 1
                            scene.clip_slots[n].has_stop_button = 1
                        n += 1
                else:
                    clip_slot.clip.muted = 1

            i += 1

        if clip_count == 0:
            self._clear_loop(scene)
        else:
            scene.fire()


    def _clear_loop(self, scene):
        for clip_slot in scene.clip_slots:
            if clip_slot.has_clip:
                if clip_slot.clip.name == "-":
                    clip_slot.has_stop_button = 0
                if not clip_slot.clip.name == "+":
                    clip_slot.delete_clip()
        scene.name = 'loop[]'


    def _stop_loop(self, scene):
        for clip_slot in scene.clip_slots:
            if clip_slot.has_clip and clip_slot.is_playing:
                clip_slot.stop()


    def _mute_loop(self, scene):
        tracks = self.parent._get_tracks_of_scene(scene)
        for track in tracks:
            track.mute = True


    def _unmute_loop(self, scene):
        tracks = self.parent._get_tracks_of_scene(scene)
        for track in tracks:
            track.mute = False

    
    def _mute_loops_by_instr(self, track):
        loop_group = self.parent._get_child_with_name(track, 'LOOPS')
        loops = self.parent._get_children(loop_group)
        for loop in loops:
            loop.mute = 1


    def _unmute_loops_by_instr(self, track):
        loop_group = self.parent._get_child_with_name(track, 'LOOPS')
        loops = self.parent._get_children(loop_group)
        for loop in loops:
            loop.mute = 0
            

    def log(self, msg):
        self.parent.log(msg)