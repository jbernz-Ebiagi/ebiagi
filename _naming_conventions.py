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

def is_send(name):
    return name.startswith('S[')

def is_ex_instrument_track(name):
    return name.startswith('X[')

def is_spine(name):
    return name == '[SPINE]'

def is_source_track(name):
    return name.endswith('[S]')

def is_trunk_track(name):
    return name.endswith('[T]')

def is_compiled_track(name):
    return name.endswith('[C]')

def is_light_track(name):
    return name.endswith('[M]')

def is_live_track(name):
    return name.endswith('[L]')

def is_loop(name):
    return name.startswith('loop[')

def is_variation(name):
    return name.startswith('variation[')

#Paired macro names follow the format: P[track_short_name][macro_name]
def is_paired_macro(name):
    return name.startswith('P[')

def get_paired_macro_params(name):
    res = re.findall(r'\[(.*?)\]', name)
    if res:
        return res
    else:
        return ''

def get_short_name(name):
    res = re.search(r"\[([A-Za-z0-9_ ,-.]+)\]", name)
    if res:
        return re.search(r"\[([A-Za-z0-9_ ,-.]+)\]", name).group(1)
    else:
        return ''

#Clip name: {NAME} COMMAND(1) COMMAND(2) COMMAND
def parse_clip_name(name):
    match = re.search('\{([^}]+)', name)
    if match is not None:
        return match.group(1)
    else:
        return None

def parse_clip_commands(name):
    words = name.split()
    commands = [word for word in words if any(keyword in word for keyword in ('PLAY', 'SNAP', 'HOLD', 'MUTE', 'STOP', 'AUM', 'SELECT', 'PQUANT', 'RETURN', 'FA_BASE'))]
    return commands

def parse_clip_command_param(command):
    match = re.search('\(([^)]+)', command)
    if match is not None:
        return match.group(1)
    else:
        return None    