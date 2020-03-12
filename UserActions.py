import functools
import traceback
import subprocess
from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase

#Provides @catch_exception decorator for debugging
def catch_exception(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            args[0].canonical_parent.log_message(traceback.format_exc())
    return func

def parse_args(s):
    return s.split(' ')


class UserActions(UserActionsBase):

    def create_actions(self):
        self.add_global_action('select_loop', self.select_loop)
        self.add_global_action('deselect_loop', self.deselect_loop)
        self.add_global_action('select_all_loops', self.select_all_loops)
        self.add_global_action('deselect_all_loops', self.deselect_all_loops)
        self.add_global_action('clear_loop', self.clear_loop)
        #self.add_global_action('clear_all_loops', self.clear_all_loops)
        self.add_global_action('stop_loop', self.stop_loop)
        #self.add_global_action('stop_all_loops', self.stop_all_loops)
        #self.add_global_action('reset_loop_params', self.reset_loop_params)
        #self.add_global_action('reset_all_loop_params', self.reset_all_loop_params)
        #self.add_global_action('mute_loop', self.mute_loop)
        #self.add_global_action('mute_all_loops', self.mute_all_loops)
        self.add_global_action('select_clip', self.select_clip)
        self.add_global_action('deselect_clip', self.deselect_clip)
        #self.add_global_action('select_fx', self.select_fx)
        #self.add_global_action('deselect_fx', self.deselect_fx)
        #self.add_global_action('reset_fx', self.reset_fx)
        #self.add_global_action('reset_all_fx', self.reset_all_fx)

        self.selected_instruments = {}
        self.held_scenes = set([])
        self._update_data()
        

    # Actions ----------------------------------------------------------------------------

    @catch_exception
    def select_loop(self, action_def, args):
        key_name = args
        scene = self._get_loop_scene(key_name)
        if(scene is not None):
            if(scene.name == 'loop[]'):
                self._create_loop(scene, key_name)
            else:
                self._select_loop(scene)
        else:
            self.log('exceeded maximum loop count')


    @catch_exception
    def deselect_loop(self, action_def, args):
        key_name = args
        scene = self._get_loop_scene(key_name)
        if(scene is not None):
            self._deselect_scene(scene)


    @catch_exception
    def select_all_loops(self, action_def, args):
        scenes = self._get_all_loops()
        if(len(scenes) > 0):
            for scene in scenes:
                self._select_loop(scene)


    @catch_exception
    def deselect_all_loops(self, action_def, args):
        scenes = [x for x in self.held_scenes if 'loop' in x.name]
        if(len(scenes) > 0):
            for scene in scenes:
                self._deselect_scene(scene)


    @catch_exception
    def clear_loop(self, action_def, args):
        key_name = args
        scene = self._get_loop_scene(key_name)
        if(scene and scene.name != 'loop[]'):
            self._clear_loop(scene)


    @catch_exception
    def stop_loop(self, action_def, args):
        key_name = args
        scene = self._get_loop_scene(key_name)
        if(scene and scene.name != 'loop[]'):
            self._stop_loop(scene)

    @catch_exception
    def select_clip(self, action_def, args):
        clip_name = args
        scene = self._get_clip_scene(clip_name)
        self._trigger_scene(scene)
        self._select_scene(scene)


    @catch_exception
    def deselect_clip(self, action_def, args):
        clip_name = args
        scene = self._get_clip_scene(clip_name)
        self._deselect_scene(scene)


    @catch_exception
    def select_fx(self, action_def, args):
        clip_name = args
        scene = self._get_clip_scene(clip_name)
        self._trigger_scene(scene)
        self._select_scene(scene)


    @catch_exception
    def deselect_fx(self, action_def, args):
        clip_name = args
        scene = self._get_clip_scene(clip_name)
        self._deselect_scene(scene)


    # Utils ------------------------------------------------------------------------------


    def _trigger_scene(self, scene):
        scene.fire()


    def _select_scene(self, scene):
        self.log('select')
        self.held_scenes.add(scene)
        self._update_data()
        self._update_selected_instruments()


    def _deselect_scene(self, scene):
        self.log('deselect')
        self.log(self.held_scenes)
        self.held_scenes.remove(scene)
        self._update_data()
        if len(self.held_scenes) > 0:
            self._update_selected_instruments()


    def _update_selected_instruments(self):
        self.log('update')
        self.selected_instruments.clear()

        for scene in self.held_scenes:
            for track_name in self._get_tracks_in_scene(scene):
                self.log(track_name)
                if not track_name in self.selected_instruments:
                    self.selected_instruments[track_name] = set([])
                if 'loop' in scene.name:
                    self.selected_instruments[track_name].add('loop')
                if 'CLIP' in scene.name:
                    self.selected_instruments[track_name].add('clip')


        for track in self.song().tracks:
            if 'INSTR' in track.name:

                loop_open = 0
                clip_open = 0

                self.log(track.name)
                if track.name in self.selected_instruments:
                    if 'loop' in self.selected_instruments[track.name]:
                        loop_open = 127
                    if 'clip' in self.selected_instruments[track.name]:
                        clip_open = 127
                    if len(self.selected_instruments) == 1:
                        self.song().view.selected_track = track

                for device in track.devices:
                    if device.can_have_chains == 1:
                        for subdevice in device.chains[0].devices:
                            if subdevice.name == 'LOOP_IN':
                                subdevice.parameters[8].value = loop_open
                            if subdevice.name == 'CLIP_IN':
                                subdevice.parameters[8].value = clip_open
                            


    def _get_tracks_in_scene(self, scene):
        tracks = []
        i = 0
        for clip_slot in scene.clip_slots:
            if self._clip_slot_has_notes(clip_slot):
                track = self.song().tracks[i]
                if track.has_midi_output:
                    tracks.append(track.output_routing_type.display_name)
            i +=1
        return tracks

    
    def _clip_slot_has_notes(self, clip_slot):
        if clip_slot.has_clip:
            clip_slot.clip.select_all_notes()
            if len(clip_slot.clip.get_selected_notes()) > 0:
                return True
        return False


    def _select_loop(self, scene):
        for clip_slot in scene.clip_slots:
            if clip_slot.has_clip and clip_slot.is_recording:
                self._finish_record(scene)
                self._select_scene(scene)
                return
            if clip_slot.has_clip and clip_slot.is_playing:
                self._select_scene(scene)
                return
        self._trigger_scene(scene)


    def _get_loop_scene(self, key_name):
        loop_name = 'loop[' + key_name + ']'
        for scene in self.song().scenes:
            if loop_name in scene.name:
                return scene
        for scene in self.song().scenes:
            if scene.name == 'loop[]':
                return scene
        return False

    
    def _create_loop(self, scene, key_name):
        scene.name = 'loop[' + key_name + ']'
        scene.fire()


    def _get_all_loops(self):
        loops = []
        for scene in self.song().scenes:
            if 'loop' in scene.name and scene.name != 'loop[]':
                loops.append(scene)
        return loops

    
    def _finish_record(self, scene):
        clip_count = 0
        for clip_slot in scene.clip_slots:
            if clip_slot.has_clip:
                clip_slot.clip.select_all_notes()
                if len(clip_slot.clip.get_selected_notes()) > 0:
                    clip_count += 1
        if clip_count == 0:
            self._clear_loop(scene)
        else:
            scene.fire()


    def _clear_loop(self, scene):
        for clip_slot in scene.clip_slots:
            if clip_slot.has_clip:
                clip_slot.delete_clip()
        scene.name = 'loop[]'


    def _stop_loop(self, scene):
        for clip_slot in scene.clip_slots:
            if clip_slot.has_clip and clip_slot.is_playing:
                clip_slot.stop()


    def _get_clip_scene(self, scene_name):
        for scene in self.song().scenes:
            if scene_name.upper() in scene.name:
                return scene
        return False

    
    def _update_data(self):
        held_scene_names = []
        for scene in self.held_scenes:
            held_scene_names.append(scene.name)
        self.song().set_data('held_scene_names', held_scene_names)



    def clyphx_trigger(self, command):
        self.canonical_parent.clyphx_pro_component.trigger_action_list(command)


    def log(self, message):
        self.canonical_parent.log_message(message)
