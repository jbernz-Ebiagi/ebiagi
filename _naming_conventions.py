import re 

def is_input(name):
    return name.startswith('IN[')

def is_midi_router(name):
    return name.startswith('MR[')

def is_audio_router(name):
    return name.startswith('AR[')

def is_module(name):
    return name.startswith('M[')
    
def is_instrument(name):
    return name.startswith('I[')

def is_ex_instrument_track(name):
    return name.startswith('X[')

def is_source_track(name):
    return name.endswith('[S]')

def is_loop(name):
    return name.startswith('loop[')
    
def get_short_name(name):
    return re.search(r"\[([A-Za-z0-9_,-.]+)\]", name).group(1)