from threading import Timer
from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase
from _utils import catch_exception
from _utils import strip_name_params

from _LoopController import LoopController
from _ClipController import ClipController
from _GlobalFXController import GlobalFXController
from _CbordController import CbordController


class GlobalActions(UserActionsBase):

    @catch_exception
    def create_actions(self):

        self.loop = LoopController(self)
        self.clip = ClipController(self)
        self.gfx = GlobalFXController(self)
        self.cbord = CbordController(self)

        self.selected_instrument = None
        self.selected_fx = set([])

        self.virtual_tree = []
        self._update_virtual_tree()

        self._update_data()

        self.saved_params = {}
        Timer(1.5, self._save_current_params).start()
        

    # Actions ----------------------------------------------------------------------------




    # Utils ------------------------------------------------------------------------------


    def _trigger_scene(self, scene):
        scene.fire()


    def _select_instrument(self, track):
        self.selected_instrument = track
        self.selected_fx = set([])
        self._update_selection()
        self.show_audio_swift()


    def _select_fx(self, track):
        self.selected_instrument = None
        self.selected_fx.add(track)
        self._update_selection()
        self.show_audio_swift()


    def _deselect_fx(self, track):
        if len(self.selected_fx) > 1:
            self.selected_fx.remove(track)
            self._update_selection()
        else:
            self.selected_fx.remove(track)


    def _update_selection(self):
        for track in self.song().tracks:

            #Instr
            if track.name == 'CTRL_IN':
                if track == self.selected_instrument:
                    track.arm = 1
                    instrument_track = self._get_child_with_name(self._get_parent(self._get_parent(track)), 'INSTR')
                    self.song().view.selected_track = instrument_track
                else:
                    track.arm = 0


            #Loop, GFX
            if track.name == 'FX' or 'GFX' in track.name:
                is_selected = False
                if track in self.selected_fx:
                    track.arm = 1
                    self.song().view.selected_track = track
                else:
                    track.arm = 0

        self._update_data()


    def _update_data(self):
        if self.selected_instrument:
            self.song().set_data('selected_instrument_group', self._get_parent(self._get_parent(self.selected_instrument)).name)
        else:
            self.song().set_data('selected_instrument_group', None)

        selected_fx_groups = []
        for track in self.selected_fx:
            selected_fx_groups.append(self._get_parent(track).name)
        self.song().set_data('selected_fx_groups', selected_fx_groups)
                    

    def _get_tracks_of_scene(self, scene):
        tracks = []
        i = 0
        for clip_slot in scene.clip_slots:
            if self._clip_slot_has_notes(clip_slot):
                tracks.append(self.song().tracks[i])
            i +=1
        return tracks


    def _get_track_with_name(self, name):
        for track in self.song().tracks:
            if strip_name_params(track.name) == name:
                return track
        return False


    def _clip_slot_has_notes(self, clip_slot):
        if clip_slot.has_clip and clip_slot.clip.is_midi_clip:
            clip_slot.clip.select_all_notes()
            if len(clip_slot.clip.get_selected_notes()) > 0:
                return True
        return False


    @catch_exception
    def _save_current_params(self):
        current_params = {}
        for track in self.song().tracks:
            if track.name == 'INSTR' or track.name == 'FX' or 'GFX' in track.name:
                group_name = self._get_parent(track).name
                for device in track.devices:
                    current_params[group_name + '_' + track.name] = {}
                    for i in range(1,9):
                        current_params[group_name + '_' + track.name][i] = device.parameters[i].value
        self.saved_params = current_params


    def _update_virtual_tree(self):

        for track in self.song().tracks:
            if track.is_foldable:
                if track.is_grouped:
                    track.fold_state = 1
                else:
                    track.fold_state = 0

        tree = []
        current_scope = []
        i = 0

        for track in self.song().tracks:

            if track.is_foldable:
                n = i + 1
                children = []
                parent = None
                #second level group
                if track.is_grouped:
                    parent = current_scope[0]
                    while n < len(self.song().tracks) and not self.song().tracks[n].is_visible:
                        children.append(self.song().tracks[n])
                        n += 1
                #top level group
                else:
                    while n < len(self.song().tracks) and self.song().tracks[n].is_grouped:
                        if self.song().tracks[n].is_visible:
                            children.append(self.song().tracks[n])
                        n += 1
                tree.append({
                    'track': track,
                    'parent': parent,
                    'children': children
                })
                if not track.is_grouped:
                    current_scope = []
                    current_scope.append(track)
                else:
                    if len(current_scope) == 2:
                        current_scope[1] = track
                    else:
                        current_scope.append(track)
            else:
                if not track.is_grouped:
                    current_scope = []
                if track.is_grouped and track.is_visible and len(current_scope) == 2:
                    current_scope.pop(1)
                if current_scope[-1]:
                    parent = current_scope[-1]
                else:
                    parent = None
                tree.append({
                    'track': track,
                    'parent': parent,
                    'children': None
                })

            i += 1

        self.virtual_tree = tree

        for track in self.song().tracks:
            if track.is_foldable:
                track.fold_state = 1

    
    def _get_child_with_name(self, track, name):
        for vtrack in self.virtual_tree:
            if track == vtrack['track']:
                if vtrack['children']:
                    for ctrack in vtrack['children']:
                        if strip_name_params(ctrack.name) == name:
                            return ctrack
        return None


    def _get_children(self, track):
        children = []
        for vtrack in self.virtual_tree:
            if track == vtrack['track']:
                if vtrack['children']:
                    for ctrack in vtrack['children']:
                        children.append(ctrack)
        return children
    

    def _get_parent(self, track):
        for vtrack in self.virtual_tree:
            if track == vtrack['track']:
                return vtrack['parent']


    def show_audio_swift(self):
        self.clyphx_trigger("""
            SHOWDEV ;
            KEY ESC ;
            KEY ALT DN ;
            KEY STRIKE ;
            KEY FLUSH ;        
        """)


    def clyphx_trigger(self, command):
        self.canonical_parent.clyphx_pro_component.trigger_action_list(command)


    def log(self, message):
        self.canonical_parent.log_message(message)