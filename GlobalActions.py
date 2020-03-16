import functools
import traceback
import subprocess
from threading import Timer
from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase

from _LoopActions import LoopActions
from _ClipActions import ClipActions
from _FXActions import FXActions
from _CbordActions import CbordActions


def catch_exception(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            args[0].canonical_parent.log_message(traceback.format_exc())
    return func


class GlobalActions(UserActionsBase):

    @catch_exception
    def create_actions(self):

        self.loop_actions = LoopActions(self)
        self.clip_actions = ClipActions(self)
        self.fx_actions = FXActions(self)
        self.cbord_actions = CbordActions(self)

        self.selected_instruments = {}
        self.held_scenes = set([])
        self.held_fx = set([])
        self.cbord_inputs = []
        #self._update_cbord_inputs()
        self._update_data()

        self.saved_params = {}
        Timer(0.5, self._save_current_params).start()
        

    # Actions ----------------------------------------------------------------------------



    # Utils ------------------------------------------------------------------------------


    def _trigger_scene(self, scene):
        scene.fire()


    def _select_scene(self, scene):
        self.held_scenes.add(scene)
        self._update_data()
        self._update_selected_instruments()


    def _deselect_scene(self, scene):
        self.log(self.held_scenes)
        self.held_scenes.remove(scene)
        if len(self.held_scenes) + len(self.held_fx) > 0:
            self._update_data()
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

                if track.name in self.selected_instruments:
                    if 'loop' in self.selected_instruments[track.name]:
                        loop_open = 127
                    if 'clip' in self.selected_instruments[track.name]:
                        clip_open = 127
                    if len(self.held_fx) == 0 and len(self.selected_instruments) == 1:
                        self.song().view.selected_track = track

                for device in track.devices:
                    if device.can_have_chains == 1:
                        for subdevice in device.chains[0].devices:
                            if subdevice.name == 'LOOP_IN':
                                subdevice.parameters[8].value = loop_open
                            if subdevice.name == 'CLIP_IN':
                                subdevice.parameters[8].value = clip_open
            if track.name == 'FX':
                self.log(track.devices)
                if len(self.held_fx) == 1 and len(self.selected_instruments) == 0:
                    self.song().view.selected_track = track
                for device in track.devices:
                    if device in self.held_fx:
                        device.parameters[8].value = 127
                    else:
                        device.parameters[8].value = 0
                    

    #loop tracks
    def _get_tracks_of_scene(self, scene):
        tracks = []
        i = 0
        for clip_slot in scene.clip_slots:
            if self._clip_slot_has_notes(clip_slot):
                tracks.append(self.song().tracks[i])
            i +=1
        return tracks


    #instr track names
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


    def _save_current_params(self):
        current_params = {}
        for track in self.song().tracks:
            if 'INSTR' in track.name:
                current_params[track.name] = {}
                for i in range(5,9):
                    self.log(track.devices[0].parameters[i].name)
                    current_params[track.name][i] = track.devices[0].parameters[i].value
            if track.name == 'FX':
                for device in track.devices:
                    current_params[device.name] = {}
                    for i in range(1,9):
                        current_params[device.name][i] = device.parameters[i].value
        self.saved_params = current_params

    
    def _update_data(self):
        held_scene_names = []
        for scene in self.held_scenes:
            held_scene_names.append(scene.name)
        self.song().set_data('held_scene_names', held_scene_names)

        held_fx_names = []
        for device in self.held_fx:
            held_fx_names.append(device.name)
        self.song().set_data('held_fx_names', held_fx_names)


    def clyphx_trigger(self, command):
        self.canonical_parent.clyphx_pro_component.trigger_action_list(command)


    def log(self, message):
        self.canonical_parent.log_message(message)


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