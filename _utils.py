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

def strip_name_params(name):
    if name.find('[') != -1:
        return name[0:name.find('[')].strip()
    return name

def is_module(track):
    return track.name.startswith('M[')

def is_midi_input(track, midi_input_names):
    return track.name.replace('_IN','') in midi_input_names

def is_instrument(track):
    return track.name.startswith('I[')

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
