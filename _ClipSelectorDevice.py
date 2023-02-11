from functools import partial
import math
from ._EbiagiComponent import EbiagiComponent
from ._naming_conventions import *
import Live
import threading

class ClipSelectorDevice(EbiagiComponent):

    def __init__(self, device, instrument):
        super(ClipSelectorDevice, self).__init__()
        self._device = device
        self._instrument = instrument

        self.quantization_knob = self.get_quantization_knob()
        self._device.view.add_selected_chain_listener(self.on_selected_chain_change)

        self.interval = threading.Timer(5.0, self.refresh_track_selection)
        self.interval.start()
        self.lock = False

    def on_selected_chain_change(self):
        for i, clip_slot in enumerate(self._instrument._track.clip_slots):
            if clip_slot.has_clip:
                if parse_clip_name(clip_slot.clip.name) == self._device.view.selected_chain.name:
                    clips = self.get_instrument_clips_at_index(self._instrument, i)
                    quantization = math.floor(self.quantization_knob.value)
                    self.midi_action(partial(self.trigger_clips_with_quantiaztion, clips, quantization))

    def trigger_clips_with_quantiaztion(self, clips, quantization):
        if self.lock:
            return
        self.lock = True
        return_quantization = math.floor(clips[0].launch_quantization)
        for clip in clips:
            clip.launch_quantization = quantization
        self.midi_action(partial(self.finish_clips_trigger, clips, return_quantization))

    def finish_clips_trigger(self, clips, return_quantization):
        for clip in clips:
            clip.legato = 1
            if self._device.is_active:
                clip.fire()
            clip.launch_quantization = return_quantization
            self.lock = False

    def get_instrument_clips_at_index(self, instrument, i):
        clips = []
        for track in instrument._ex_tracks:
            if track.clip_slots[i].has_clip:
                clips.append(track.clip_slots[i].clip)
        return clips

    def get_quantization_knob(self):
        for param in self._device.parameters:
            if param.name == 'QUANTIZATION':
                return param

    def refresh_track_selection(self):
        device = self.canonical_parent.song().view.selected_track
        self.canonical_parent.song().view.selected_track = self._instrument._track
        self.canonical_parent.song().view.selected_track = device
        # self.interval = threading.Timer(5.0, self.refresh_track_selection)
        # self.interval.start()

    def disconnect(self):
        super(ClipSelectorDevice, self).disconnect()
        self._device.view.remove_selected_chain_listener(self.on_selected_chain_change)
        self.interval.cancel()

