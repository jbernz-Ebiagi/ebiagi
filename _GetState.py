def get_state(Set):
    if Set and not Set.loading:

        modules = []
        loops = []
        clips = []
        instr = []
        inputs = {}
        mfx = []
        gfx = []
        global_loops = []
        snaps = []
        metronome = Set._song.metronome > 0

        for module in Set.modules:
            color = color_name(module.track.color_index)
            brightness = 1 if module is Set.active_module else 0
            modules.append({
                'index': Set.modules.index(module),
                'color': color, 
                'brightness': brightness,
            })

        for instrument in Set.active_module.instruments:
            color = color_name(instrument.track.color_index)
            brightness = 1 if instrument.is_armed() else 0
            instr.append({
                'index': Set.active_module.instruments.index(instrument),
                'color': color, 
                'brightness': brightness,
            })

        return {
            'instr': instr,
            'inputs': inputs,
            'modules': modules,
            'loops': loops,
            'clips': clips,
            'mfx': mfx,
            'gfx': gfx,
            'globalLoops': global_loops,
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
        69: 'maroon',
        13: 'white',
        59: 'gold',
        1: 'orange',
        20: 'teal',
        24: 'purple',
        55: 'white'
    }
    return color_index_map[index]