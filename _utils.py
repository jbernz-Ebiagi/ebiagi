import functools
import traceback
import subprocess

def catch_exception(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            args[0].log(traceback.format_exc())
    return func

def is_module(track):
    return track.name.startswith('M[')

def is_instrument(track):
    return track.name.startswith('I[')

def is_input(track):
    return '_IN' in track.name

def set_input_routing(track, routing_name):
    for routing in track.available_input_routing_types:
        if routing.display_name == routing_name:
            track.input_routing_type = routing
            return

def is_loop_track(track):
    return track.name == 'LOOP'

def get_loop_key(name):
    return name[len('loop['):-len(']')]

def set_output_routing(track, routing_name):
    for routing in track.available_output_routing_types:
        if routing.display_name == routing_name:
            track.output_routing_type = routing

def is_loop_scene(scene):
    return 'loop' in scene.name

def is_midi_channel(track):
    return 'MIDI_CHANNEL' in track.name

def is_audio_channel(track):
    return 'AUDIO_CHANNEL' in track.name

def is_mpe_track(track):
    return 'MPE' in track.name

def is_mpe_loop(track):
    return track.name == 'MPE_LOOP'

def strip_name_params(name):
    if name.find('[') != -1:
        return name[0:name.find('[')].strip()
    return name



def is_midi_input(track, midi_input_names):
    return track.name.replace('_IN','') in midi_input_names and track.has_midi_output

def is_audio_input(track, audio_input_names):
    return track.name.replace('_IN','') in audio_input_names and track.has_audio_output



def is_module_fx(track):
    return track.name.startswith('MFX')

def is_gfx(track):
    return track.name.startswith('GFX')

def is_cbord_in(track):
    return track.name == 'CBORD_IN'

def is_as_in(track):
    return track.name == 'AS_IN'

def is_nanok_in(track):
    return track.name == 'NANOK_IN'
    
def is_clip_track(track):
    return track.name == 'CLIP'

def is_instr(track):
    return track.name == 'INSTR'

def is_loop_track(track):
    return track.name == 'LOOP'

def is_loop_scene(scene):
    return 'loop' in scene.name

def index_of_loop_scene(name, scenes):
    i = 0
    for scene in scenes:
        if 'loop[' + name + ']' == scene.name:
            return i

def is_locked(clip):
    return 'lock' in clip.name

def is_empty_clip(clip):
    if clip.is_midi_clip:
        clip.select_all_notes()
        if len(clip.get_selected_notes()) > 0 or clip.has_envelopes:
            return False
    if clip.is_audio_clip:
        return False
    return True


def is_record(track):
    return track.name == 'RECORD'



def set_output_routing(track, routing_name):
    for routing in track.available_output_routing_types:
        if routing.display_name == routing_name:
            track.output_routing_type = routing

# def is_mpe_track(track):
#     return 'MPE' in track.input_routing_type.display_name

def set_mpe_output_channel(track):
    channel = int(track.input_routing_type.display_name.replace('_IN','')[-1])
    if track.available_output_routing_channels[channel+1]:
        track.output_routing_channel = track.available_output_routing_channels[channel+1]

def is_metronome(track):
    return track.name == 'METRO'

color_index_map = {
    9: 'blue',
    12: 'pink',
    39: 'lavender',
    56: 'red',
    61: 'green',
    69: 'maroon',
    13: 'white',
    59: 'gold',
    1: 'orange',
    20: 'teal',
    24: 'purple',
}

def color_name(index):
    return color_index_map[index]
