from _Instrument import Instrument, MidiInstrument, AudioInstrument
from _utils import catch_exception, set_output_routing

class Loop:

    @catch_exception
    def __init__(self, Set):
        self.set = Set

        self.midi_track = None
        self.midi_clip_slot = None

        self.audio_track = None
        self.audio_clip_slot = None

        self.mpe_tracks = []
        self.mpe_clip_slots = []

        self.instrument = None

    def all_clip_slots(self):
        return [self.midi_clip_slot, self.audio_clip_slot] + self.mpe_clip_slots

    def set_clip(self, clip_slot):
        if clip_slot.clip.is_audio_clip:
            clip_slot.duplicate_clip_to(self.audio_clip_slot)
        elif clip_slot.clip.is_midi_clip:
            clip_slot.duplicate_clip_to(self.midi_clip_slot)

    def clear_clips(self):
        for clip_slot in self.all_clip_slots():
            if clip_slot.has_clip:
                clip_slot.delete_clip()

    def set_instrument(self, instrument):
        self.instrument = instrument
        if isinstance(instrument, MidiInstrument):
            self.midi_track.devices[0].parameters[1].value = instrument.channel.track.devices[0].parameters[1].value
        elif isinstance(instrument, AudioInstrument):
            channel_number = int(instrument.channel.track.name[-1])
            channel_send = self.audio_track.mixer_device.sends[channel_number-1]
            channel_send.value = channel_send.max

    def clear_instrument(self):
        self.instrument = None
        self.midi_track.devices[0].parameters[1].value = 127
        for channel_send in self.audio_track.mixer_device.sends:
            channel_send.value = channel_send.min

    def is_playing(self):
        for clip_slot in self.all_clip_slots():
            if clip_slot.is_playing: 
                return True
        return False

    def is_recording(self):
        for clip_slot in self.all_clip_slots():
            if clip_slot.is_recording: 
                return True
        return False


    def log(self, msg):
        self.module.log(msg)