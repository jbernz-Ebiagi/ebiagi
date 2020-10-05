from _utils import catch_exception, set_output_routing, is_empty_clip
from _Instrument import AudioInstrument

class Clip:

    @catch_exception
    def __init__(self, Set):
        self.set = Set

        self.midi_track = None
        self.midi_clip_slot = None

        self.audio_track = None
        self.audio_clip_slot = None

        self.midi_stop_clip = None
        self.audio_stop_clip = None

        self.instrument = None

    def all_clip_slots(self):
        return [self.midi_clip_slot, self.audio_clip_slot]

    def clear(self):
        self.instrument = None
        self.midi_track.devices[0].parameters[1].value = 0
        for channel_send in self.audio_track.mixer_device.sends:
            channel_send.value = channel_send.min
        for clip_slot in self.all_clip_slots():
            if clip_slot.has_clip:
                clip_slot.delete_clip()

    def is_playing(self):
        for clip_slot in self.all_clip_slots():
            if clip_slot.is_playing: 
                return True
        return False

    def has_clip(self):
        for clip_slot in self.all_clip_slots():
            if clip_slot.has_clip:
                return True
        return False

    def play(self):
        for clip_slot in self.all_clip_slots():
            if clip_slot.has_clip:

                if 'GATE' in clip_slot.clip.name:
                    self.instrument.mute_loops()

                if 'SELECT' in clip_slot.clip.name:
                    idx = self.set.active_module.instruments.index(self.instrument)
                    self.set.select_instrument(idx)

                clip_slot.fire()

    def stop(self):
        for clip_slot in self.all_clip_slots():
            if clip_slot.has_clip:

                if 'GATE' in clip_slot.clip.name:
                    self.instrument.unmute_loops()
                    
                if 'SELECT' in clip_slot.clip.name:
                    idx = self.set.active_module.instruments.index(self.instrument)
                    self.module.deselect_instrument(idx)

                if 'THRU' in clip_slot.clip.name:
                    return

        self.midi_stop_clip.fire()
        self.audio_stop_clip.fire()

    def log(self, msg):
        self.module.log(msg)