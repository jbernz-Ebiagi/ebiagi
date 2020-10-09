from _utils import catch_exception, set_output_routing, is_empty_clip, get_loop_key, on_same_row
from _Instrument import AudioInstrument

class Loop:

    @catch_exception
    def __init__(self, Set, name):
        self.set = Set
        self.name = name

        self.midi_track = None
        self.midi_clip_slot = None

        self.audio_track = None
        self.audio_clip_slot = None

        self.instrument = None

    def all_clip_slots(self):
        return [self.midi_clip_slot, self.audio_clip_slot]

    def clear(self):
        if self.instrument:
            self.instrument.deactivate_loop_in_router(self.midi_channel())
            self.instrument = None
        for router_send in self.audio_track.mixer_device.sends:
            router_send.value = router_send.min
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
            self.log(self.set.held_instruments)
            if len(self.set.held_instruments) > 0:
                self.check_exclusive()
                self.record()
        elif self.is_playing():
            # for clip_slot in self.all_clip_slots():
            #     if clip_slot.is_playing:
            #         self.module.set.base.song().view.detail_clip = clip_slot.clip
            #         self.module.set.base.canonical_parent.application().view.show_view('Detail/Clip')
            return
        else:
            self.check_exclusive()
            for clip_slot in self.all_clip_slots():
                if clip_slot.has_clip:
                    self.instrument.add_loop_to_router(self.midi_channel())
                    clip_slot.fire()


    def record(self):
        self.instrument = next(iter(self.set.held_instruments))
        if isinstance(self.instrument, AudioInstrument):
            self.instrument.set_loop_router(self)
            self.audio_clip_slot.fire()
            if len(self.instrument.aux_instruments) > 0:
                self.instrument.aux_instruments[0].add_loop_to_router(self.midi_channel())
                self.midi_clip_slot.fire()
        else:
            self.instrument.add_loop_to_router(self.midi_channel())
            self.midi_clip_slot.fire()

    def check_exclusive(self):
        if self.instrument and self.instrument.exclusive:
            if self.instrument.exclusive == 'HE':
                #stop all loops with a shared instrument sharing a horizontal array
                for loop in self.set.loops:
                    if self.set.loops[loop].instrument is self.instrument and on_same_row(self.name, loop):
                        self.set.loops[loop].stop()
            if self.instrument.exclusive == 'AE':
                #stop all loops with a shared instrument
                for loop in self.set.loops:
                    if self.set.loops[loop].instrument is self.instrument:
                        self.set.loops[loop].stop()

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
        if self.instrument:
            self.instrument.deactivate_loop_in_router(self.midi_channel())
        if self.is_recording():
            self.finish_record()
        else:
            for clip_slot in self.all_clip_slots():
                if clip_slot.has_clip:
                    clip_slot.stop()

    def midi_channel(self):
        return self.midi_track.devices[0].parameters[1].value


    def log(self, msg):
        self.set.log(msg)