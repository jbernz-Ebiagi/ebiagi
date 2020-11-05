from _EbiagiComponent import EbiagiComponent
from _naming_conventions import *
from _utils import is_empty_midi_clip

class Loop(EbiagiComponent):

    def __init__(self, track, scene, Set, instruments):
        super(Loop, self).__init__()
        self._track = track
        self._scene = scene
        self._set = Set

        s = list(self._song.scenes).index(scene)
        self._main_clip_slot = track.clip_slots[s]
        self._clip_slots = []

        self.short_name = get_short_name(scene.name)

        self.log('Initializing Loop %s %s...' % (get_short_name(track.name), self.short_name))

        i = list(self._song.tracks).index(track) + 1
        while not is_module(self._song.tracks[i].name) and self._song.tracks[i].is_grouped:
            instr = None
            for instrument in instruments:
                if instrument.has_track(self._song.tracks[i]):
                    instr = instrument
            clip_slot = ClipSlot(self._song.tracks[i].clip_slots[s], self._song.tracks[i], instr, Set)
            self._clip_slots.append(clip_slot)
            i += 1

    def select(self):
        if self.is_recording():
            self._finish_record()
        elif self.is_playing():
            #self.display_first_clip()
            return
        else:
            self._main_clip_slot.fire()
            for clip_slot in self._clip_slots:
                clip_slot.run_select_commands()

    def deselect(self):
        for clip_slot in self._clip_slots:
            clip_slot.run_deselect_commands()

    def stop(self):
        if self.is_recording():
            self._finish_record()
        for clip_slot in self._clip_slots:
            clip_slot.stop()

    def clear(self):
        for clip_slot in self._clip_slots:
            if clip_slot.is_clearable():
                clip_slot.clear()

    def _finish_record(self):
        has_clip = False
        for clip_slot in self._clip_slots:
            if clip_slot.is_recording():
                if clip_slot.finish_record():
                    has_clip = True
        if not has_clip:
            self.clear()

    def can_record(self):
        will_record = False
        for clip_slot in self._clip_slots:
            if clip_slot.will_record_on_start():
                will_record = True
        return will_record or self._main_clip_slot.is_recording
    
    def color(self):
        return self._main_clip_slot.color_index or 'none'

    def is_playing(self):
        return self._main_clip_slot.is_playing

    def is_recording(self):
        return self._main_clip_slot.is_recording

    def display_first_clip(self):
        for clip_slot in self._clip_slots:
            if clip_slot.has_clip:
                self.module.set.base.song().view.detail_clip = clip_slot.clip
                self.module.set.base.canonical_parent.application().view.show_view('Detail/Clip')
                return



#Wrapper for clip_slot to add its track
class ClipSlot:

    def __init__(self, slot, track, instrument=None, Set=None):
        self._slot = slot
        self._track = track
        self._instrument = instrument
        self._set = Set

    #(because clip_slot.will_record_on_start does not work)
    def will_record_on_start(self):
        return not self._slot.has_clip and self._slot.has_stop_button and self._track.arm

    def stop(self):
        self._slot.stop()

    def is_clearable(self):
        return self._slot.has_clip and 'CAN_CLEAR' in self._slot.clip.name

    def is_recording(self):
        return self._slot.is_recording

    def finish_record(self):
        self._slot.clip.name = 'CAN_CLEAR'
        if self._slot.clip.is_midi_clip:
            if is_empty_midi_clip(self._slot.clip):
                self.deactivate_clip()
                return False
        if self._slot.clip.is_audio_clip:
            if not self._instrument.audio_in_armed():
                self.deactivate_clip()
                return False
        self._slot.fire()
        return True

    def deactivate_clip(self):
        self._slot.clip.muted = 1
        self._slot.has_stop_button = 0

    def clear(self):
        if self._slot.has_clip:
            self._slot.delete_clip()
            self._slot.has_stop_button = 1

    def run_select_commands(self):
        if self._slot.has_clip:
            if 'SELECT' in self._slot.clip.name:
                self._set.select_instrument(None, self._instrument)
                self._set.deselect_instrument(None, self._instrument)
    
    def run_deselect_commands(self):
        if self._slot.has_clip:
            if 'HOLD' in self._slot.clip.name and self._slot.is_playing:
                list(self._track.clip_slots)[-1].fire(launch_quantization=0)


