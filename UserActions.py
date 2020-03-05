import functools
import traceback
import subprocess
#import mido
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

def parse_args(s):
    return s.split(' ')


state_channel_map = {
    'empty': 1,
    'recording': 2,
    'active': 3,
    'inactive': 4
}

loop_to_midi_note = range(14,26) + range(28, 40) + range(42,53) + range(55,65)

class UserActions(UserActionsBase):

    def create_actions(self):
        self.add_global_action('start_rgb_monitor', self.start_rgb_monitor)
        self.add_global_action('select_loop', self.select_loop)
        self.add_global_action('clear_loop', self.clear_loop)
        

    # Actions ----------------------------------------------------------------------------

    @catch_exception
    def start_rgb_monitor(self, action_def, args):
        self.update_all_loop_rgb()


    @catch_exception
    def select_loop(self, action_def, args):
        loop_name = args.replace('"', '')
        for scene in self.song().scenes:
            if scene.name == loop_name:
                self.trigger_loop(scene)
                self.on_next_beat(self.update_loop_rgb, scene)


    @catch_exception
    def clear_loop(self, action_def, args):
        loop_name = args.replace('"', '')
        for scene in self.song().scenes:
            if scene.name == loop_name:
                self.delete_loop_clips(scene)
                self.on_next_beat(self.update_loop_rgb, scene)
        

    # Utils -------------------------------------------------------------------------------

    def on_next_beat(self, func, args):
        self.log('on next beat')
        currentPlayTime = self.song().get_current_smpte_song_time(0)
        hours = currentPlayTime.hours
        minutes = currentPlayTime.minutes
        seconds = currentPlayTime.seconds
        ms = currentPlayTime.frames
        currentMs = hours*60*60*1000 + minutes*60*1000 + seconds*1000 + ms
        msPerBeat = 60/self.song().tempo*1000
        msUntilNextBeat = (currentMs % msPerBeat)*10

        Timer(msUntilNextBeat/1000, func, [args]).start()


    def update_all_loop_rgb(self):
        self.log('update_all_loop_rgb')
        i = 0
        messages = []
        for scene in self.song().scenes:
            if 'LOOP' in scene.name:
                loop_state = self.get_loop_state(scene)
                messages.append("MIDIA NOTE %s %s %s" % (state_channel_map[loop_state], loop_to_midi_note[i], 1))
                i += 1
        for message in messages:
            self.clyphx_trigger(message)
        self.log('sent loop update')


    def update_loop_rgb(self, scene):
        self.log('update_loop_rgb')
        loop_state = self.get_loop_state(scene)
        i = int(scene.name[-1]) - 1
        self.canonical_parent._send_midi((state_channel_map[loop_state], loop_to_midi_note[i], 1))
        self.log('sent loop update')


    def get_loop_state(self, scene):
        for clip_slot in scene.clip_slots:
            if clip_slot.is_recording:
                self.log('RECORDING')
                return 'recording'
            if clip_slot.is_playing:
                return 'active'
            if clip_slot.has_clip:
                return 'inactive'
        return 'empty'


    def get_loop_color(self, scene):
        most_notes = 0
        current_color = 0
        for clip_slot in scene.clip_slots:
            if clip_slot.has_clip:
                if clip_slot.clip.is_midi_clip:
                    if len(clip_slot.clip.get_notes()) > most_notes:
                        most_notes = len(clip_slot.clip.get_notes())
                        current_color = clip_slot.clip.color_index
        return current_color

    
    def trigger_loop(self, scene):
        scene.fire()


    def delete_loop_clips(self, scene):
        for clip_slot in scene.clip_slots:
            if clip_slot.has_clip:
                clip_slot.delete_clip()


    def clyphx_trigger(self, command):
        self.canonical_parent.clyphx_pro_component.trigger_action_list(command)


    def log(self, message):
        self.canonical_parent.log_message(message)

    def updateRgbFile(self, file):
        self.log(file)