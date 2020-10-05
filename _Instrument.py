import math
from _Scheduler import schedule
from _utils import catch_exception, set_input_routing

class MidiInstrument:

    @catch_exception
    def __init__(self, track, module, channel):
        self.module = module
        self.track = track
        self.channel = channel
        self.aux_instruments = []
        self.is_aux = False

        #track name is of the format 'I[INSTRUMENT_NAME].input_name.loop_type
        self.input_names = self.track.name.split('.')[1].split(',')

        set_input_routing(self.track, self.channel.track.name)

    def activate(self):
        if len(self.track.devices) > 0:
            self.track.devices[0].parameters[0].value = 1
        self.channel.current_instrument = self

    def deactivate(self):
        self.track.arm = 0
        if len(self.track.devices) > 0:
           self.track.devices[0].parameters[0].value = 0
        self.channel.disarm()
        self.channel.current_instrument = None

    def has_clip(self, index):
        for instr in self.aux_instruments:
            if instr.has_clip(index):
                return True
        return self.track.clip_slots[index].has_clip

    def transfer_clip(self, loop, index):
        self.track.clip_slots[index].duplicate_clip_to(loop.midi_track.clip_slots[index])

    def set_loop_channel(self, loop):
        loop.midi_track.devices[0].parameters[1].value = self.channel.track.devices[0].parameters[1].value
        loop.instrument = self

    def arm(self):
        self.channel.arm(self.input_names)
        self.module.set.base.song().view.selected_track = self.track
        self.module.set.base.canonical_parent.application().view.show_view('Detail/DeviceChain')

    def disarm(self):
        self.channel.disarm()

    def log(self, msg):
        self.module.log(msg)


class AudioInstrument(MidiInstrument):

    @catch_exception
    def __init__(self, track, module, channel):
        MidiInstrument.__init__(self, track, module, channel)

    def transfer_clip(self, loop, index):
        if self.track.clip_slots[index].has_clip:
            self.track.clip_slots[index].duplicate_clip_to(loop.audio_track.clip_slots[index])
        if len(self.aux_instruments) > 0 and self.aux_instruments[0].has_clip(index):
            self.aux_instruments[0].track.clip_slots[index].duplicate_clip_to(loop.midi_track.clip_slots[index])

    def set_loop_channel(self, loop):
        channel_number = int(self.channel.track.name[-1])
        channel_send = loop.audio_track.mixer_device.sends[channel_number-1]
        channel_send.value = channel_send.max
        if len(self.aux_instruments) > 0:
            loop.midi_track.devices[0].parameters[1].value = self.aux_instruments[0].channel.track.devices[0].parameters[1].value
        loop.instrument = self

class MPEInstrument(MidiInstrument):

    @catch_exception
    def __init__(self, track, module, channel):
        MidiInstrument.__init__(self, track, module, channel)

    def transfer_clip(self, loop, index):
        if self.track.clip_slots[index].has_clip:
            self.track.clip_slots[index].duplicate_clip_to(loop.mpe_clip_slots[0])
        i = 1
        for mpe_aux in self.aux_instruments:
            if mpe_aux.track.clip_slots[index].has_clip:
                mpe_aux.track.clip_slots[index].duplicate_clip_to(loop.mpe_clip_slots[i])
            i += 1

    def set_loop_channel(self, loop):
        loop.mpe_tracks[0].devices[0].parameters[1].value = self.channel.track.devices[0].parameters[1].value
        i = 1
        for mpe_aux in self.aux_instruments:
            loop.mpe_tracks[i].devices[0].parameters[1].value = mpe_aux.channel.track.devices[0].parameters[1].value
        i += 1
        loop.instrument = self

#Hidden instrument used for routing midi to another instrument, place after the parent instrument
class AuxInstrument(MidiInstrument):
    def __init__(self, track, module, channel):
        MidiInstrument.__init__(self, track, module, channel)
        self.is_aux = True

    def transfer_clip(self, loop, index):
        #Don't call this, call from parent
        return False