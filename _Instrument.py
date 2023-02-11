from functools import partial
from threading import Timer
from ._EbiagiComponent import EbiagiComponent
from ._naming_conventions import *
from ._utils import set_input_routing, set_output_routing, set_output_light_channel
from _Framework.ControlSurface import get_control_surfaces
from ._BeatSelectorDevice import BeatSelectorDevice
from ._ClipSelectorDevice import ClipSelectorDevice
import math
import Live

class Instrument(EbiagiComponent):

    def __init__(self, track, Set, Module=None):
        super(Instrument, self).__init__()
        self._track = track
        self._set = Set
        self._module = Module

        self._ex_tracks = []

        self._input = None

        self.short_name = get_short_name(track.name.split('.')[0])

        # self.log('Initializing Instrument %s...' % self.short_name)

        if len(track.name.split('.')) > 1: 
            input_name = get_short_name(track.name.split('.')[1])
            try:
                self._input = Set.get_input(input_name)
            except:
                self.log('Unable to locate input: %s', input_name)

        self.clip_selectors = []
        self.beat_selectors = []
        self._create_beat_selectors(self._track.devices)
        self._create_clip_selectors(self._track.devices)
            
        #Add Ex Tracks
        i = list(self._song.tracks).index(track) + 1
        while i < len(self._song.tracks) and is_ex_instrument_track(self._song.tracks[i].name):
            self._ex_tracks.append(self._song.tracks[i])
            i += 1

        #Assign Routing
        for track in [self._track] + self._ex_tracks:
            self._assign_routing(track)

        self.paired_macros = []

    def _create_beat_selectors(self, devices):
        for device in devices:
            if device.name == 'BEAT_SELECTOR' and device.can_have_chains:
                self.beat_selectors.append(BeatSelectorDevice(device, self))
            if device.can_have_chains:
                for chain in device.chains:
                    self._create_beat_selectors(chain.devices)

    def _create_clip_selectors(self, devices):
        for device in devices:
            if device.name == 'CLIP_SELECTOR' and device.can_have_chains:
                self.clip_selectors.append(ClipSelectorDevice(device, self))
            if device.can_have_chains:
                for chain in device.chains:
                    self._create_clip_selectors(chain.devices)

    def _assign_routing(self, track):
        if is_source_track(track.name):
            set_input_routing(track, 'No Input')
            set_output_routing(track, self._track.name)
        elif is_trunk_track(track.name):
            set_input_routing(track, 'No Input')
        elif is_compiled_track(track.name):
            set_input_routing(track, self._track.name)
        elif is_light_track(track.name):
            set_output_routing(track, 'MASK')
            set_output_light_channel(track, get_short_name(track.name.split('.')[0]))
        else:
            if(self._input and (self._input.has_midi_input or self._input.has_audio_input)):
                set_input_routing(track, self._input._track.name)

    def activate(self):
        if len(self._track.devices) > 0:
            if(self.get_instrument_device()):
                self.get_instrument_device().parameters[0].value = 1
            for clip_slot in self._track.clip_slots:
                if clip_slot.has_clip and clip_slot.clip.name == 'INIT':
                    clip_slot.fire()
            for track in [self._track] + self._ex_tracks:
                self.set_default_monitoring_state(track)
            # Timer(0.5, partial(self.pair_macros, self._module.instruments)).start()
            self.pair_macros(self._module.instruments)

    def deactivate(self):
        if len(self._track.devices) > 0:
            if(self.get_instrument_device()):
                self.get_instrument_device().parameters[0].value = 0
            for pm in self.paired_macros:
                pm['link'].clear()
            self.paired_macros = []
            for track in [self._track] + self._ex_tracks:
                if track.can_be_armed:
                    track.arm = 0 

    def select(self):
        self._song.view.selected_track = self._track
        if self._input:
            self._input.set_instrument(self)

    # def deselect(self):
    #    self.input.remove_instrument(self)

    def get_instrument_device(self):
        for device in self._track.devices:
            if device.can_have_chains:
                return device

    def pair_macros(self, instruments):
        i = 1
        params = self.get_instrument_device().parameters
        #for all macros
        while i < len(params):
            param_A = params[i]
            ##if it is a paired macro
            if is_paired_macro(param_A.name):
                #for all instruments in list passed in
                for instrument in instruments:
                    #for all tracks for that instrument
                    for track in [instrument._track] + instrument._ex_tracks:
                        #if the short names match
                        if get_paired_macro_params(param_A.name) and get_short_name(track.name) == get_paired_macro_params(param_A.name)[0]:
                            for device in track.devices:
                                if device.can_have_chains:
                                    for param_B in device.parameters:
                                        if param_B.name == get_paired_macro_params(param_A.name)[1]:
                                            for s in get_control_surfaces():
                                                if s.__class__.__name__ == 'ParameterMidiLink':
                                                    self.paired_macros.append(
                                                        {
                                                            'linking_param': param_A,
                                                            'link': s.link_parameters(param_A, param_B),
                                                            'color': track.color_index
                                                        })
            i += 1

    def get_paired_macro(self, param):
        for pm in self.paired_macros:
            if pm['linking_param'] == param:
                return pm
        return False

    def arm(self):
        self.log('arm')
        for track in [self._track] + self._ex_tracks:
            if track.can_be_armed and track.input_routing_type.display_name == self._input._track.name:
                track.arm = 1

    def disarm(self):
        self.log('disarm')
        for track in [self._track] + self._ex_tracks:
            if track.can_be_armed and track.input_routing_type.display_name == self._input._track.name:
                track.arm = 0

    def is_armed(self):
        return False

    def has_track(self, track):
        return track in [self._track] + self._ex_tracks

    def has_midi_input(self):
        return len(self._midi_inputs) > 0

    def has_audio_input(self):
        return len(self._audio_inputs) > 0

    def is_selected(self):
        return self in self._set.held_instruments

    def audio_in_armed(self):
        return self._input.has_instrument(self) and self._input.is_active()

    def stop(self):
        for track in [self._track] + self._ex_tracks:
            track.stop_all_clips()     

    def mute_loops(self):
        for track in [self._track] + self._ex_tracks:
            if not is_source_track(track.name) and not is_light_track(track.name):
                if track.can_be_armed:
                    track.current_monitoring_state = 0
                    track.arm = 0
                else:
                    track.mute = 1

    def unmute_loops(self):
        for track in [self._track] + self._ex_tracks:
            track.mute = 0
            self.set_default_monitoring_state(track)

    def clear_arrangement_envelopes(self):
        for track in [self._track] + self._ex_tracks:
            for clip in track.arrangement_clips:
                if clip.has_envelopes:
                    clip.clear_all_envelopes()

    def set_default_monitoring_state(self, track):
        if not track.can_be_armed:
            return
        if is_source_track(track.name):
            track.current_monitoring_state = 2
        elif is_trunk_track(track.name):
            track.current_monitoring_state = 0
            if track.can_be_armed:
                track.arm = 0
        elif is_compiled_track(track.name):
            track.current_monitoring_state = 0
            if track.can_be_armed:
                track.arm = 0
        elif is_light_track(track.name):
            if track.can_be_armed:
                track.current_monitoring_state = 0
                track.arm = 0
        else:
            track.current_monitoring_state = 1
            if track.can_be_armed:
                track.arm = 0
    
    def disconnect(self):
        super(Instrument, self).disconnect()
        for pm in self.paired_macros:
            pm['link'].clear()
        for selector in self.clip_selectors + self.beat_selectors:
            selector.disconnect()