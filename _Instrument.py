import math
from _Scheduler import schedule
from _utils import catch_exception, set_input_routing

class MidiInstrument:

    @catch_exception
    def __init__(self, track, module, router):
        self.module = module
        self.track = track
        self.router = router
        self.aux_instruments = []
        self.is_aux = False
        self.exclusive = False

        #track name is of the format 'I[INSTRUMENT_NAME].input_name.loop_type
        attributes = self.track.name.split('.')
        self.input_names = attributes[1].split(',')
        if len(attributes) >= 3:
            self.exclusive = attributes[2]
        

        set_input_routing(self.track, self.router.track.name)

    def activate(self):
        if len(self.track.devices) > 0:
            self.track.devices[0].parameters[0].value = 1
        self.router.current_instrument = self

    def deactivate(self):
        if len(self.track.devices) > 0:
           self.track.devices[0].parameters[0].value = 0
        self.router.disarm()
        self.router.current_instrument = None

    def has_clip(self, index):
        for instr in self.aux_instruments:
            if instr.has_clip(index):
                return True
        return self.track.clip_slots[index].has_clip

    def transfer_clip(self, loop, index):
        self.track.clip_slots[index].duplicate_clip_to(loop.midi_track.clip_slots[index])
        loop.instrument = self

    def add_loop_to_router(self, loop):
        self.router.add_loop(loop)

    def deactivate_loop_in_router(self, loop):
        self.router.deactivate_loop(loop)

    def arm(self):
        self.router.arm(self.input_names)
        # self.module.set.base.song().view.selected_track = self.track
        # self.module.set.base.canonical_parent.application().view.show_view('Detail/DeviceChain')

    def disarm(self):
        self.router.disarm()

    def mute_loops(self):
        for loop in self.module.set.loops:
            if self.module.set.loops[loop].instrument is self:
                self.module.set.loops[loop].mute()

    def unmute_loops(self):
        for loop in self.module.set.loops:
            if self.module.set.loops[loop].instrument is self:
                self.module.set.loops[loop].unmute()

    def log(self, msg):
        self.module.log(msg)


class AudioInstrument(MidiInstrument):

    @catch_exception
    def __init__(self, track, module, router):
        MidiInstrument.__init__(self, track, module, router)

    def transfer_clip(self, loop, index):
        if self.track.clip_slots[index].has_clip:
            self.track.clip_slots[index].duplicate_clip_to(loop.audio_track.clip_slots[index])
        if len(self.aux_instruments) > 0 and self.aux_instruments[0].has_clip(index):
            self.aux_instruments[0].track.clip_slots[index].duplicate_clip_to(loop.midi_track.clip_slots[index])
        loop.instrument = self
        self.set_loop_router(loop)

    def set_loop_router(self, loop):
        router_number = int(self.router.track.name[-1])
        router_send = loop.audio_track.mixer_device.sends[router_number-1]
        router_send.value = router_send.max

    def add_loop_to_router(self, loop):
        if len(self.aux_instruments) > 0:
            self.aux_instruments[0].router.add_loop(loop)

    def deactivate_loop_in_router(self, loop):
        if len(self.aux_instruments) > 0:
            self.aux_instruments[0].router.deactivate_loop(loop)

    def arm(self):
        self.router.arm(self.input_names)
        if len(self.aux_instruments) > 0:
            self.aux_instruments[0].arm()
        # self.module.set.base.song().view.selected_track = self.track
        # self.module.set.base.canonical_parent.application().view.show_view('Detail/DeviceChain')

    def disarm(self):
        self.router.disarm()
        if len(self.aux_instruments) > 0:
            self.aux_instruments[0].disarm()


#Hidden instrument used for routing midi to another instrument, place after the parent instrument
class AuxInstrument(MidiInstrument):
    def __init__(self, track, module, router):
        MidiInstrument.__init__(self, track, module, router)
        self.is_aux = True

    def transfer_clip(self, loop, index):
        #Don't call this, call from parent
        return False