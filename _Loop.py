from _Instrument import Instrument
from _utils import catch_exception, is_module, is_instrument, is_locked, is_empty_clip

class Loop:

    @catch_exception
    def __init__(self, main_clip_slot, instr_clip_slots, Module):
        self.module = Module
        self.main_clip_slot = main_clip_slot
        #instr_clip_slot = {'clip_slot': --, 'instrument': --, 'mfx': --, 'track': --}
        self.instr_clip_slots = instr_clip_slots
        self.type = None

    def select(self):
        instruments = self.get_instruments()
        mfx = self.get_mfx()
        if self.main_clip_slot.is_recording:
            self.finish_record()
        elif self.main_clip_slot.is_playing:
            for instrument in instruments:
                self.module.select_instrument(module.instruments.index(instrument))
        else:
            for i in self.instr_clip_slots:
                clip_slot = i['clip_slot']
                #Don't record if it will stop another clip
                if not clip_slot.has_clip and clip_slot.has_stop_button and i['track'].playing_slot_index > -1:
                    clip_slot.create_clip(1)
                else:
                    if len(instruments) + len(mfx) <= 1 or \
                    len(self.module.held_instruments) + len(self.module.held_mfx) == 0 or \
                    i['instrument'] in self.module.held_instruments or \
                    i['mfx'] in self.module.held_mfx: #multi clip loop
                        i['clip_slot'].fire()

    def deselect(self):
        for instrument in self.get_instruments():
            self.module.deselect_instrument(self.module.instruments.index(instrument))

    def stop(self):
        if self.main_clip_slot.is_recording:
            self.finish_record()
        else:
            for i in self.instr_clip_slots:
                clip_slot = i['clip_slot']
                if clip_slot.has_clip:
                    clip_slot.stop()

    def clear(self):
        if not self.is_locked():
            for i in self.instr_clip_slots:
                if i['clip_slot'].has_clip:
                    i['clip_slot'].delete_clip()
                    i['clip_slot'].has_stop_button = 1

    def finish_record(self):
        clip_count = 0
        for i in self.instr_clip_slots:
            clip_slot = i['clip_slot']
            if clip_slot.has_clip:
                if (clip_slot.clip.is_midi_clip and not is_empty_clip(clip_slot.clip)) or \
                (clip_slot.clip.is_audio_clip and i['instrument'].get_input('LINE').arm == 1):
                    clip_slot.fire()
                    clip_count += 1
                else:
                    clip_slot.has_stop_button = 0
                    clip_slot.clip.muted = 1
        if clip_count == 0:
            self.clear()

    def get_instruments(self):
        instruments = set([])
        for i in self.instr_clip_slots:
            if i['clip_slot'].has_clip:
                if not is_empty_clip(i['clip_slot'].clip) and i['instrument']:
                    instruments.add(i['instrument'])
        return instruments

    def get_mfx(self):
        mfx = set([])
        for i in self.instr_clip_slots:
            if i['clip_slot'].has_clip:
                if not is_empty_clip(i['clip_slot'].clip) and i['mfx']:
                    mfx.add(i['mfx'])
        return mfx

    def is_locked(self):
        for i in self.instr_clip_slots:
            if i['clip_slot'].has_clip and is_locked(i['clip_slot'].clip):
                return True
        else:
            return False

    def log(self, msg):
        self.module.log(msg)