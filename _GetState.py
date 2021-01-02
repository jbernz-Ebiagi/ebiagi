def get_state(Set):
    if Set and not Set.loading:

        modules = []
        loops = []
        clips = []
        instr = []
        inputs = {}
        mfx = []
        ginstr = []
        globalLoop = None
        snaps = []
        metronome = Set._song.metronome > 0

        for ipt in Set.inputs.values():       
            if len(ipt._instruments) > 1:
                inputs[ipt.short_name] = 'white'
            elif len(ipt._instruments) == 1:
                inputs[ipt.short_name] = color_name(next(iter(ipt._instruments))._track.color_index)
            elif ipt.phantom_instrument:
                inputs[ipt.short_name] = color_name(ipt.phantom_instrument._track.color_index)
            else:
                inputs[ipt.short_name] = 'dark'
            if ipt._track.mute == 1:
                inputs[ipt.short_name] = 'dark'

        for module in Set.modules:
            color = color_name(module._track.color_index)
            brightness = 1 if module is Set.active_module else 0
            modules.append({
                'index': Set.modules.index(module),
                'color': color, 
                'brightness': brightness,
            })

        for instrument in Set.active_module.instruments:
            color = color_name(instrument._track.color_index)
            brightness = 1 if instrument.is_armed() else 0
            instr.append({
                'index': Set.active_module.instruments.index(instrument),
                'color': color, 
                'brightness': brightness,
            })

        for key in Set.active_module.loops:
            loop = Set.active_module.loops[key]
            color = 'red' if loop.can_record() and not loop.has_clips() or loop.is_recording() else color_name(loop.color())
            brightness = 1 if loop.is_playing() else 0
            loops.append({
                'key_name': key,
                'color': color, 
                'brightness': brightness,
            })   


        for snap in Set.active_module.snaps:
            color = 'blue' if snap is Set.snap_control.selected_snap else 'white'
            brightness = 1 if len(snap.snap_params) > 0 else 0
            snaps.append({
                'index': Set.active_module.snaps.index(snap),
                'color': color, 
                'brightness': brightness,
            })

        for global_instrument in Set.global_instruments:
            brightness = 1 if global_instrument.is_armed() else 0
            ginstr.append({
                'index': Set.global_instruments.index(global_instrument),
                'color': 'white', 
                'brightness': brightness, 
            })

        global_loop = {
            'color': 'red' if Set.global_loop.is_recording else 'white', 
            'brightness': 1 if Set.global_loop.is_playing else 0,
        }


        return {
            'instr': instr,
            'inputs': inputs,
            'modules': modules,
            'loops': loops,
            'clips': clips,
            'mfx': mfx,
            'ginstr': ginstr,
            'globalLoop': global_loop,
            'snaps': snaps,
            'metronome': metronome
        }

    else:
        return 'no active set'

def color_name(index):
    color_index_map = {
        9: 'blue',
        12: 'pink',
        39: 'lavender',
        56: 'red',
        61: 'green',
        69: 'white',
        13: 'white',
        59: 'gold',
        1: 'orange',
        20: 'teal',
        24: 'purple',
        55: 'white',
        'none': 'dark'
    }
    return color_index_map[index]