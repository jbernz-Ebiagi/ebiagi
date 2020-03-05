import functools
import traceback
import subprocess
from threading import Timer
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


class MyActions(UserActionsBase):

    def create_actions(self):
        self.held_fx_devices = 0

        self.add_clip_action('toggle_trigger', self.toggle_trigger_clip)
        self.add_clip_action('if_clip_playing', self.if_clip_playing)
        self.add_track_action('create_snap', self.create_snap)

        self.add_track_action('select_fx_device', self.select_fx_device)
        self.add_track_action('release_fx_device', self.release_fx_device)
        self.add_track_action('select_instrument_group', self.select_instrument_group)
        self.add_track_action('reset_fx_device_params', self.reset_fx_device_params)
        self.add_track_action('mute_loops', self.mute_loops)
        self.add_track_action('unmute_loops', self.unmute_loops)
        self.add_track_action('arm_group', self.arm_group)
        self.add_track_action('delete_group_clip', self.delete_group_clip)
        self.add_global_action('show_audio_swift', self.show_audio_swift)

        self.add_global_action('hide_midi_groups', self.hide_midi_groups)

        self.add_global_action('load_set', self.load_set)
        self.add_global_action('assign_seaboard', self.assign_seaboard)

    # Actions ----------------------------------------------------------------------------

    def toggle_trigger_clip(self, action_def, args):
        clip = action_def['clip']
        self.canonical_parent.log_message('called method')
        if clip:
            if clip.is_playing:
                clip.stop()
            else:
                clip.fire()

    @catch_exception
    def if_clip_playing(self, action_def, args):
        track = action_def['track']
        clip = action_def['clip']

        track_index = list(self.song().tracks).index(track)
        if clip:
            clip_index = 0
            i = 0
            for clip_slot in track.clip_slots:
                if clip_slot.clip == clip:
                    clip_index = i
                i += 1
            if clip.is_playing:
                self.canonical_parent.log_message("%s/CLIP(%s) %s" % (track_index+1, clip_index+1, args))
                self.canonical_parent.clyphx_pro_component.trigger_action_list("%s/CLIP(%s) %s" % (track_index+1, clip_index+1, args))

    def create_snap(self, action_def, args):
        SNAP_TRACK = action_def['track'].name
        SNAP_NAME = args

        self.canonical_parent.clyphx_pro_component.trigger_action_list("""
            "%s"/SEL; 
            SCENE SEL LAST; 
            "%s"/CLIP(SEL) DEL; 
            "%s"/ADDCLIP; 
            "%s"/CLIP LOOP OFF;
            "%s"/CLIP NAME "[%s] ALL/SNAP DEV(1)";
            "%s"/PLAYQ NONE SEL;
        """ % (SNAP_TRACK, SNAP_TRACK, SNAP_TRACK, SNAP_TRACK, SNAP_TRACK, SNAP_NAME, SNAP_TRACK))


    @catch_exception
    def select_fx_device(self, action_def, args):
        device_index = int(args)
        fx_track = action_def['track']

        if self.held_fx_devices == 0:        
            self.disarm_all_as_inputs({})

        self.held_fx_devices += 1       
        fx_track.devices[device_index+1].parameters[8].value = 127    

        self.song().view.selected_track = fx_track
        self.show_audio_swift(action_def, args)


    @catch_exception
    def release_fx_device(self, action_def, args):
        device_index = int(args)
        fx_track = action_def['track']

        self.held_fx_devices -= 1   

        if self.held_fx_devices > 0:
            fx_track.devices[device_index+1].parameters[8].value = 0


    @catch_exception
    def reset_fx_device_params(self, action_def, args):
        device_index = int(args)
        fx_track = action_def['track']

        for x in range(7):
            fx_track.devices[device_index+1].parameters[x+1].value = 0          


    @catch_exception
    def select_instrument_group(self, action_def, args):
        group_track = action_def['track']
        track_index = list(self.song().tracks).index(group_track)

        self.disarm_all_note_inputs({})
        self.disarm_all_as_inputs({})

        def arm_if_input_track(self, track):
            if track.name == 'NOTE_IN' or track.name == 'LOOPS' or track.name == 'AS_IN':
                track.arm = 1
        self.group_action(group_track, arm_if_input_track)

        self.song().view.selected_track = self.song().tracks[track_index+1]
        self.show_audio_swift(action_def, args)


    @catch_exception
    def mute_loops(self, action_def, args):
        group_track = action_def['track']

        def mute_if_loop_midi(self, track):
            if track.name == 'LOOPS':
                track.mute = 1

        self.group_action(group_track, mute_if_loop_midi)


    @catch_exception
    def unmute_loops(self, action_def, args):
        group_track = action_def['track']

        def mute_if_loop_midi(self, track):
            if track.name == 'LOOPS':
                track.mute = 0

        self.group_action(group_track, mute_if_loop_midi)


    def arm_group(self, action_def, args): #args = arm_state = 1 or 0
        group_track = action_def['track']
        arm_state = args

        def arm_group_track(self, track):
            if track.can_be_armed:
                track.arm = arm_state

        self.group_action(group_track, arm_group_track)


    @catch_exception
    def delete_group_clip(self, action_def, args):
        group_track = action_def['track']
        clip_index = list(self.song().scenes).index(self.song().view.selected_scene)

        def delete_clip(self, track):
            if track.clip_slots[clip_index].has_clip:
                track.clip_slots[clip_index].delete_clip()

        self.group_action(group_track, delete_clip)


    def load_set(self, action_def, args):
        self.canonical_parent.clyphx_pro_component.trigger_action_list("""
            "Master"/SEL ; 
            LOADUSER "LoadSet.adg" ; 
            WAIT 2 ; 
            "Master"/Dev("LoadSet") P%s 127
        """ % args)


    def show_audio_swift(self, action_def, args):
        self.canonical_parent.clyphx_pro_component.trigger_action_list("""
            SHOWDEV ;
            KEY ESC ;
            KEY STRIKE;
        """)

        # default_directory =  "/Users/justin/My Files/Audio/Live/Modules/"
        # subprocess.check_call(["open", default_directory + "Original/Level[-1] Project/Level[-1].als"])
        # t = Timer(0.1, self.disable_dialog)
        # t.start()


    #Select seaboard track, and pass name of output track
    def assign_seaboard(self, action_def, args):
        TARGET_TRACK_NAME = args.replace('"', '')

        if self.song().view.selected_track.name == 'MPE_MIDI':
            i = 0
            while self.song().tracks[i] != self.song().view.selected_track:
                i += 1

            SB_INPUT = [x for x in self.song().tracks[i+1].available_input_routing_types if x.display_name == "Seaboard BLOCK"][0]
            MIDI_OUTPUT = [x for x in self.song().tracks[i+1].available_output_routing_types if x.display_name == TARGET_TRACK_NAME][0]

            for x in range(16):
                self.song().tracks[i+x+1].input_routing_type = SB_INPUT
                self.song().tracks[i+x+1].input_routing_channel = self.song().tracks[i+x+1].available_input_routing_channels[x+1]
                self.song().tracks[i+x+1].output_routing_type = MIDI_OUTPUT
                self.song().tracks[i+x+1].output_routing_channel = self.song().tracks[i+x+1].available_output_routing_channels[x+2]


    @catch_exception
    def hide_midi_groups(self, action_def, args):
       for track in list(self.song().tracks):
        if track.name == 'MIDI_IN' or track.name == 'AUDIO_IN':
            track.fold_state = 1



    #UTILS ------------------------------------------------------------------

    def group_action(self, group_track, func):
        if group_track.is_foldable:
            selected_track = self.song().view.selected_track
            original_fold = group_track.fold_state
            group_track.fold_state = 1

            i = list(self.song().tracks).index(group_track)
            
            x = 1
            while not self.song().tracks[i+x].is_visible:
                func(self, self.song().tracks[i+x])
                x += 1

            group_track.fold_state = original_fold
            self.song().view.selected_track = selected_track
        else:
            self.canonical_parent.log_message('ERROR: called group_action on non-group track')

    def disable_dialog(self):
        if self.application().current_dialog_button_count == 3: 
            self.application().press_current_dialog_button(0)
        if self.application().current_dialog_button_count == 2: 
            self.application().press_current_dialog_button(1)

    def disarm_all_note_inputs(self, action_def):
        for track in self.song().tracks:
            if track.name == 'NOTE_IN' or track.name == 'LOOPS':
                track.arm = 0

    def disarm_all_as_inputs(self, action_def):
        for track in self.song().tracks:
            if track.name == 'AS_IN':
                track.arm = 0
            if track.name == 'FX' or track.name == 'MASTER_FX':
                for device in track.devices:
                    if device.can_have_chains:
                        device.parameters[8].value = 0

