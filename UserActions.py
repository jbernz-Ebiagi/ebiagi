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
        self.add_global_action('clear_loop', self.clear_loop)
        self.add_global_action('stop_loop', self.stop_loop)
        

    # Actions ----------------------------------------------------------------------------

    @catch_exception
    def select_loop(self, action_def, args):
        key_name = args
        loop = self._get_loop(key_name)
        if(loop):
            if(loop.name == 'loop[]'):
                self._create_loop(loop, key_name)
            else:
                for clip_slot in loop.clip_slots:
                    if clip_slot.has_clip and clip_slot.is_recording:
                        self._finish_record(loop)
                        return
                    if clip_slot.has_clip and clip_slot.is_playing:
                        self.log('select')
                        return
                self._trigger_loop(loop)
        else:
            self.log('exceeded maximum loop count')


    @catch_exception
    def clear_loop(self, action_def, args):
        key_name = args
        loop = self._get_loop(key_name)
        if(loop and loop.name != 'loop[]'):
            self._clear_loop(loop)


    @catch_exception
    def stop_loop(self, action_def, args):
        key_name = args
        loop = self._get_loop(key_name)
        if(loop and loop.name != 'loop[]'):
            self._stop_loop(loop)


    # Utils ------------------------------------------------------------------------------


    def _trigger_loop(self, scene):
        scene.fire()


    def _get_loop(self, key_name):
        loop_name = 'loop[' + key_name + ']'
        for scene in self.song().scenes:
            if loop_name in scene.name:
                return scene
        for scene in self.song().scenes:
            if scene.name == 'loop[]':
                return scene
        return False

    
    def _create_loop(self, loop, key_name):
        loop.name = 'loop[' + key_name + ']'
        loop.fire()

    
    def _finish_record(self, loop):
        clip_count = 0
        for clip_slot in loop.clip_slots:
            if clip_slot.has_clip:
                clip_slot.clip.select_all_notes()
                if len(clip_slot.clip.get_selected_notes()) > 0:
                    clip_count += 1
        if clip_count == 0:
            self._clear_loop(loop)
        else:
            loop.fire()


    def _clear_loop(self, loop):
        for clip_slot in loop.clip_slots:
            if clip_slot.has_clip:
                clip_slot.delete_clip()
        loop.name = 'loop[]'


    def _stop_loop(self, loop):
        for clip_slot in loop.clip_slots:
            if clip_slot.has_clip and clip_slot.is_playing:
                clip_slot.stop()


    def clyphx_trigger(self, command):
        self.canonical_parent.clyphx_pro_component.trigger_action_list(command)


    def log(self, message):
        self.canonical_parent.log_message(message)
