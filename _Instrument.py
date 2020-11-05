from functools import partial
from _EbiagiComponent import EbiagiComponent
from _naming_conventions import *
from _utils import set_input_routing, set_output_routing

class Instrument(EbiagiComponent):

    def __init__(self, track, Set):
        super(Instrument, self).__init__()
        self._track = track
        self._set = Set

        self._midi_inputs = []
        self._audio_inputs = []
        self._ex_midi = []
        self._ex_audio = []


        self._midi_router = None
        self._audio_router = None

        self.short_name = get_short_name(track.name.split('.')[0])

        self.log('Initializing Instrument %s...' % self.short_name)

        input_names = get_short_name(track.name.split('.')[1]).split(',')
        for name in input_names:
            if Set.inputs[name]:
                if Set.inputs[name].has_midi_input:
                    self._midi_inputs.append(Set.inputs[name])
                if Set.inputs[name].has_audio_input:
                    self._audio_inputs.append(Set.inputs[name])
        

        i = list(self._song.tracks).index(track) + 1
        while is_ex_instrument_track(self._song.tracks[i].name):

            #Add Ex Tracks
            if is_ex_instrument_track(self._song.tracks[i].name):
                if self._song.tracks[i].has_midi_input:
                    self._ex_midi.append(self._song.tracks[i])
                elif self._song.tracks[i].has_audio_input:
                    self._ex_audio.append(self._song.tracks[i])

            i += 1

    def activate(self):
        if len(self._track.devices) > 0:
            self._track.devices[0].parameters[0].value = 1
            for track in [self._track] + self._ex_midi + self._ex_audio:
                if track.can_be_armed:
                    track.arm = 1 

    def deactivate(self):
        if len(self._track.devices) > 0:
            self._track.devices[0].parameters[0].value = 0
            for track in [self._track] + self._ex_midi + self._ex_audio:
                if track.can_be_armed:
                    track.arm = 0 

    def select(self):
        self._song.view.selected_track = self._track
        self._assign_to_inputs()

    def deselect(self):
        self._unassign_from_inputs()

    def _assign_to_inputs(self):
        for midi_input in self._midi_inputs:
            midi_input.add_instrument(self)
        for audio_input in self._audio_inputs:
            audio_input.add_instrument(self)

    def _unassign_from_inputs(self):
        for midi_input in self._midi_inputs:
            midi_input.remove_instrument(self)
        for audio_input in self._audio_inputs:
            audio_input.remove_instrument(self)
            
    def set_midi_router(self, router):
        self._midi_router = router
        router.set_instrument(self)
        if self._track.has_midi_input:
            self._assign_to_router(self._track, router)
        for track in self._ex_midi:
            self._assign_to_router(track, router)

    def set_audio_router(self, router):
        self._audio_router = router
        router.set_instrument(self)
        if self._track.has_audio_input:
            self._assign_to_router(self._track, router)
        for track in self._ex_audio:
            self._assign_to_router(track, router)

    def _assign_to_router(self, track, router):
        if is_source_track(track.name):
            set_output_routing(track, router._track.name)
        else:
            set_input_routing(track, router._track.name)

    def is_armed(self):
        return False

    def has_track(self, track):
        return track in [self._track] + self._ex_midi + self._ex_audio

    def has_midi_input(self):
        return len(self._midi_inputs) > 0

    def has_audio_input(self):
        return len(self._audio_inputs) > 0

    def audio_in_armed(self):
        for ipt in self._audio_inputs:
            if ipt.has_instrument(self) and ipt.is_active():
                return True
        return False

    def mute_loops(self):
        for track in [self._track] + self._ex_midi + self._ex_audio:
            if not is_source_track(track.name):
                track.current_monitoring_state = 0

    def unmute_loops(self):
        for track in [self._track] + self._ex_midi + self._ex_audio:
            if not is_source_track(track.name):
                track.current_monitoring_state = 1