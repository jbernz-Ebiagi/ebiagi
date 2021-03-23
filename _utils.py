import functools
import traceback

def catch_exception(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            args[0].log(traceback.format_exc())
    return func

def clear_log_file():
    open('/Users/justin/Library/Preferences/Ableton/Live 11.0.1/Log.txt', 'w').close()

def set_input_routing(track, routing_name):
    for routing in track.available_input_routing_types:
        if routing.display_name == routing_name:
            track.input_routing_type = routing
            return

def set_output_routing(track, routing_name):
    for routing in track.available_output_routing_types:
        if routing.display_name == routing_name:
            track.output_routing_type = routing

def is_empty_midi_clip(clip):
    if clip.is_midi_clip:
        clip.select_all_notes()
        if len(clip.get_selected_notes()) > 0 or clip.has_envelopes:
            return False
    if clip.is_audio_clip:
        return False
    return True

qwerty_order = ['1','2','3','4','5','6','7','8','9','0','-','equal','q','w','e','r','t','y','u','i','o','p','lb','rb','a','s','d','f','g','h','j','k','l','semi','apos','z','x','c','v','b','n','m',',','.','slash']