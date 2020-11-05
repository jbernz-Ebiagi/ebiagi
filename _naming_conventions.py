import re 

def is_input(name):
    return name.startswith('IN[')

def is_midi_router(name):
    return name.startswith('MR[')

def is_audio_router(name):
    return name.startswith('AR[')

def is_global_instrument(name):
    return name.startswith('GI[')

def is_global_loop_track(name):
    return name == 'GLOBAL_LOOP'

def is_snap_control(name):
    return get_short_name(name) == 'SNAP_CONTROL'

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
    res = re.search(r"\[([A-Za-z0-9_ ,-.]+)\]", name)
    if res:
        return re.search(r"\[([A-Za-z0-9_ ,-.]+)\]", name).group(1)
    else:
        return None