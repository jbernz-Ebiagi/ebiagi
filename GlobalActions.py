from threading import Timer
from time import clock
from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase
from _utils import catch_exception
from _utils import strip_name_params

from _LoopController import LoopController
from _ClipController import ClipController
from _GlobalFXController import GlobalFXController
from _CbordController import CbordController
from _EnvClipController import EnvClipController


class GlobalActions(UserActionsBase):

    @catch_exception
    def create_actions(self):

        # self.loop = LoopController(self)
        # self.clip = ClipController(self)
        # self.gfx = GlobalFXController(self)
        # self.cbord = CbordController(self)
        # self.envClip = EnvClipController(self)

        self.selected_cbord_instr = None
        self.selected_as_fx = set([])

        self.virtual_tree = []
        # self._update_virtual_tree()

        # self.add_global_action('assign_all_as', self.assign_all_as)
        # self.add_global_action('deselect_all_as', self.deselect_all_as)
        

    # Actions ----------------------------------------------------------------------------

    @catch_exception
    def assign_all_as(self, action_def, args):
        self.log('select all start')
        self.time = clock()
        for track in self.song().tracks:
            if track.name == 'AS_IN' or 'GFX' in track.name:
                self.selected_as_fx.add(track)
        self.log('update selection')
        self.log(clock() - self.time)
        self._update_selection()
        self.log('show audio swift')
        self.log(clock() - self.time)
        self.show_audio_swift()
        self.log('finish select all')
        self.log(clock() - self.time)


    #can be optimized
    @catch_exception
    def deselect_all_as(self, action_def, args):
        self.selected_as_fx = set([])


    # Utils ------------------------------------------------------------------------------


    def _trigger_scene(self, scene):
        scene.fire()


    def _assign_cbord(self, track):
        self.selected_cbord_instr = track

        routing_group = self._get_parent(track)
        as_in = self._get_child_with_name(routing_group, 'AS_IN')
        self.selected_as_fx.add(as_in)

        self.log(routing_group)

        instrument_track = self._get_child_with_name(self._get_parent(routing_group), 'INSTR')
        self.song().view.selected_track = instrument_track

        self._update_selection()


    def _assign_as(self, track):
        self.selected_as_fx.add(track)

        if('GFX' in track.name):
            self.song().view.selected_track = track
        else:
            instrument_track = self._get_child_with_name(self._get_parent(self._get_parent(track)), 'INSTR')
            self.song().view.selected_track = instrument_track

        self._update_selection()


    def _update_selection(self):
        self.log(self.selected_as_fx)
        for track in self.song().tracks:
            if track.name == 'CBORD_IN' or track.name == 'AS_IN' or 'GFX' in track.name:
                if track == self.selected_cbord_instr or track in self.selected_as_fx:
                    self.log('wee')
                    track.arm = 1
                else:
                    self.log('woo')
                    track.arm = 0


    def _deselect_as(self, track):
        if len(self.selected_as_fx) > 1:
            self.selected_as_fx.remove(track)
            self._update_selection()
        else:
            self.selected_as_fx.remove(track) 
                    

    def _get_tracks_of_scene(self, scene):
        tracks = []
        i = 0
        for clip_slot in scene.clip_slots:
            if clip_slot.has_clip:
                if self._clip_slot_has_notes(clip_slot) or clip_slot.clip.has_envelopes:
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