from _utils import catch_exception, set_output_routing, is_empty_clip
from _Instrument import AudioInstrument, MPEInstrument

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

    def clear(self):
        self.instrument = None
        self.midi_track.devices[0].parameters[1].value = 0
        for mpe_track in self.mpe_tracks:
            mpe_track.devices[0].parameters[1].value = 0
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

    def is_recording(self):
        for clip_slot in self.all_clip_slots():
            if clip_slot.is_recording: 
                return True
        return False

    def has_clip(self):
        for clip_slot in self.all_clip_slots():
            if clip_slot.has_clip:
                return True
        return False

    def select(self):
        if self.is_recording():
            self.finish_record()
        elif not self.has_clip():
            if len(self.set.held_instruments) > 0:
                self.record()
        elif self.is_playing():
            for clip_slot in self.all_clip_slots():
                if clip_slot.is_playing:
                    self.module.set.base.song().view.detail_clip = clip_slot.clip
                    self.module.set.base.canonical_parent.application().view.show_view('Detail/Clip')
                    return
        else:
            for clip_slot in self.all_clip_slots():
                if clip_slot.has_clip:
                    clip_slot.fire()

    def record(self):
        next(iter(self.set.held_instruments)).set_loop_channel(self)
        if isinstance(self.instrument, AudioInstrument):
            self.audio_clip_slot.fire()
            if len(self.instrument.aux_instruments) > 0:
                self.midi_clip_slot.fire()
        elif isinstance(self.instrument, MPEInstrument):
            for clip_slot in self.mpe_clip_slots:
                clip_slot.fire()
        else:
            self.midi_clip_slot.fire()


    def finish_record(self):
        for clip_slot in self.all_clip_slots():
            if clip_slot.has_clip:
                if clip_slot.clip.is_midi_clip and is_empty_clip(clip_slot.clip):
                    clip_slot.delete_clip()
                else:
                    clip_slot.fire()
        if not self.has_clip():
            self.clear()     

    def stop(self):
        if self.is_recording():
            self.finish_record()
        else:
            for clip_slot in self.all_clip_slots():
                if clip_slot.has_clip:
                    clip_slot.stop()

    def log(self, msg):
        self.module.log(msg)