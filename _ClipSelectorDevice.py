from functools import partial
import math
from ._EbiagiComponent import EbiagiComponent
from ._naming_conventions import *
import Live

class ClipSelectorDevice(EbiagiComponent):

    def __init__(self, device, instrument):
        super(ClipSelectorDevice, self).__init__()
        self._device = device
        self._instrument = instrument

        self.select_knob = self.get_select_knob()
        self.quantization_knob = self.get_quantization_knob()

        self.select_knob.add_value_listener(self.on_select_knob_change)

        self.variations = self.get_variations()

        self.lock = False

    def on_select_knob_change(self):
        if not self._device.is_active or self._instrument._track.playing_slot_index < 0:
            return
        clips = []
        selected_variation = self.get_selected_variation()
        for track in [self._instrument._track] + self._instrument._ex_tracks:
            for i, clip_slot in enumerate(track.clip_slots):
                if clip_slot.has_clip:
                    if parse_clip_name(clip_slot.clip.name) == selected_variation:
                        clips.append(clip_slot.clip)
        if len(clips) > 0:
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
            l = clip.legato
            clip.legato = 1
            if self._device.is_active and not clip.is_playing and clip:
                clip.fire()
            clip.legato = l
            clip.launch_quantization = return_quantization
            self.lock = False

    def get_select_knob(self):
        for param in self._device.parameters:
            if param.name == 'CLIP SELECT':
                return param

    def get_quantization_knob(self):
        for param in self._device.parameters:
            if param.name == 'QUANTIZATION':
                return param

    def get_variations(self):
        variations = []
        for param in self._device.parameters:
            if param.name != 'Device On' and param.name != 'CLIP SELECT' and param.name != 'QUANTIZATION' and not param.name.startswith('Macro'):
                variations.append(param)
        return variations

    def get_selected_variation(self):
        variations = self.variations       
        current_variation = variations[0]
        selected_value = self.select_knob.value
        for v in self.variations:
            if v.value <= selected_value and v.value > current_variation.value:
                current_variation = v
        return current_variation.name

    def disconnect(self):
        super(ClipSelectorDevice, self).disconnect()
        self.select_knob.remove_value_listener(self.on_selected_knob_change)

