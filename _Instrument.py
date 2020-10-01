import math
from _Scheduler import schedule
from _utils import catch_exception, set_input_routing

class Instrument:

    @catch_exception
    def __init__(self, track, module, channel):
        self.module = module
        self.track = track
        self.channel = channel

        #track name is of the format 'I[INSTRUMENT_NAME].input_name.loop_type
        self.input_names = self.track.name.split('.')[1].split(',')
        set_input_routing(self.track, self.channel.track.name)

    def activate(self):
        if len(self.track.devices) > 0:
            self.track.devices[0].parameters[0].value = 1
        self.channel.assign(self)

    def deactivate(self):
        self.track.arm = 0
        if len(self.track.devices) > 0:
           self.track.devices[0].parameters[0].value = 0
        self.channel.clear()

    def has_clip(self, index):
        return self.track.clip_slots[index].has_clip

    def transfer_clip(self, loop, index):
        self.track.clip_slots[index].duplicate_clip_to(loop.midi_track.clip_slots[index])

    def log(self, msg):
        self.module.log(msg)



class MidiInstrument(Instrument):

    @catch_exception
    def __init__(self, track, module, channel):
        Instrument.__init__(self, track, module, channel)



class AudioInstrument(Instrument):

    @catch_exception
    def __init__(self, track, module, channel):
        Instrument.__init__(self, track, module, channel)

    def transfer_clip(self, loop, index):
        if self.track.clip_slots[index].has_clip:
            self.track.clip_slots[index].duplicate_clip_to(loop.audio_track.clip_slots[index])


class MPEInstrument(MidiInstrument):

    @catch_exception
    def __init__(self, track, module, channel):
        MidiInstrument.__init__(self, track, module, channel)
        
        self.mpe_tracks = []

    def has_clip(self, index):
        for track in self.mpe_tracks:
            if track.clip_slots[index].has_clip:
                return True
        return self.track.clip_slots[index].has_clip

    def transfer_clip(self, loop, index):
        if self.track.clip_slots[index].has_clip:
            self.track.clip_slots[index].duplicate_clip_to(loop.midi_track.clip_slots[index])
        i = 0
        for track in self.mpe_tracks:
            if track.clip_slots[index].has_clip:
                track.clip_slots[index].duplicate_clip_to(loop.mpe_tracks[i].clip_slots[index])
            i += 1