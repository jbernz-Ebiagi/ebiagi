import math

def get_state(Set):
    if Set and not Set.loading:
        active_modules = {} 
        modules = []
        loops = {}
        clips = []
        instr = []
        inputs = {}
        mfx = []
        ginstr = []
        globalLoop = None
        snaps = []
        sections = []
        metronome = Set._song.metronome > 0
        beat = 0
        measure = 0
        module_name = None
        knobs = []

        module_name = Set.targetted_module._track.name

        for ipt in Set.midi_inputs + Set.audio_inputs:       
            if ipt.selected_instrument != None:
                inputs[ipt.short_name] = color_name(ipt.selected_instrument._track.color_index)
            else:
                inputs[ipt.short_name] = 'dark'
            if not ipt.is_active():
                inputs[ipt.short_name] = 'dark'

        for module in Set.modules:
            color = color_name(module._track.color_index)
            brightness = 1 if module is Set.targetted_module else 0
            modules.append({
                'index': Set.modules.index(module),
                'color': color, 
                'brightness': brightness,
            })

        for instrument in Set.targetted_module.instruments:
            color = color_name(instrument._track.color_index)
            brightness = 1 if instrument.is_armed() else 0
            instr.append({
                'index': Set.targetted_module.instruments.index(instrument),
                'color': color, 
                'brightness': brightness,
            })

        for key in Set.targetted_module.loops:
            loop = Set.targetted_module.loops[key]
            color = 'red' if loop.can_record() and not loop.has_clips() or loop.is_recording() else color_name(loop.color())
            brightness = 0
            if loop.is_playing():
                brightness = 1
            if loop.is_triggered():
                brightness = 3     
            loops[key] = {
                'color': color, 
                'brightness': brightness,
            }

        for section in Set.targetted_module.sections:
            color = color_name(section.color())
            brightness = 0
            if section.is_playing():
                brightness = 1
            if section.is_triggered():
                brightness = 3    
            sections.append({
                'index': Set.targetted_module.sections.index(section),
                'color': color, 
                'brightness': brightness,
            })   

        # for snap in Set.targetted_module.snaps:
        #     color = 'blue' if snap is Set.snap_control.selected_snap else 'white'
        #     brightness = 1 if len(snap.snap_params) > 0 else 0
        #     snaps.append({
        #         'index': Set.targetted_module.snaps.index(snap),
        #         'color': color, 
        #         'brightness': brightness,
        #     })

        for global_instrument in Set.global_instruments:
            brightness = 1 if global_instrument.is_armed() else 0
            ginstr.append({
                'index': Set.global_instruments.index(global_instrument),
                'color': 'white', 
                'brightness': brightness, 
            })

        active_crossfade = Set.active_crossfade

        smart_record = {
            'color': 'red',
            'brightness': 1 if Set.smart_loop and Set.smart_loop.is_recording() else 0
        }

        woot_arp = {
            # 'rate': Set.woot._track.devices[0].parameters[0].value
            # 'style': Set.woot._track.devices[0].parameters[1].value
            'device_on': Set.woot._track.devices[0].parameters[7].value
        } if Set.woot else {}

        if Set.active_modules['A'] != None:
            active_modules['A'] = {
                'color': color_name(Set.active_modules['A']._track.color_index)
            }
        if Set.active_modules['B'] != None:
            active_modules['B'] = {
                'color': color_name(Set.active_modules['B']._track.color_index)
            }
        if Set._song.is_playing:
            beat = round(Set._song.current_song_time % Set._song.signature_numerator + 1, 2)
            measure = math.floor(Set._song.current_song_time / Set._song.signature_numerator + 1)

        return {
            'instr': instr,
            'inputs': inputs,
            'modules': modules,
            'loops': loops,
            'clips': clips,
            'mfx': mfx,
            'ginstr': ginstr,
            'active_crossfade': active_crossfade,
            # 'snaps': snaps,
            'sections': sections,
            'metronome': metronome,
            'smart_record': smart_record,
            'woot_arp': woot_arp,
            'active_modules': active_modules,
            'beat': beat,
            'measure': measure,
            'module_name': module_name,
            'knobs': knobs
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