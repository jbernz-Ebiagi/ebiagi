from ._EbiagiComponent import EbiagiComponent
from ._naming_conventions import *
from ._utils import is_empty_midi_clip
from functools import partial
import Live
import math

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

        # self.log('Initializing Loop %s %s...' % (get_short_name(track.name), self.short_name))

        i = list(self._song.tracks).index(track) + 1
        while not is_module(self._song.tracks[i].name) and self._song.tracks[i].is_grouped:
            instr = None
            for instrument in instruments:
                if instrument.has_track(self._song.tracks[i]):
                    instr = instrument
            if instr:
                clip_slot = ClipSlot(self._song.tracks[i].clip_slots[s], self._song.tracks[i], instr, Set)
                self._clip_slots.append(clip_slot)
            i += 1

    def select(self):
        if self.is_recording():
            self._finish_record()
        # elif self.is_playing():
        #     self.display_first_clip()
        #     for clip_slot in self._clip_slots:
        #         clip_slot.run_select_commands()
        #     return
        else:
            #self._main_clip_slot.fire()
            has_clip = False
            for clip_slot in self._clip_slots:
                if clip_slot.has_clip():
                    has_clip = True
            for clip_slot in self._clip_slots:
                #don't record if there are already clips
                if not (clip_slot.will_record_on_start() and has_clip):
                    if len(clip_slot._clip_commands) > 0:
                        clip_slot.run_select_commands()
                    # elif not self.is_playing():
                    #     clip_slot.fire()
                    else:
                        clip_slot.fire()

    def deselect(self):
        for clip_slot in self._clip_slots:
            clip_slot.run_deselect_commands()

    def stop(self):
        if self.is_recording():
            self._finish_record()
        for clip_slot in self._clip_slots:
            if not clip_slot.is_group_clip():
                if self.is_triggered():
                    clip_slot.stop()
                    #self._track.stop_all_clips()
                else:
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

    def quantize(self):
        for clip_slot in self._clip_slots:
            clip_slot.quantize()

    def can_record(self):
        will_record = False
        for clip_slot in self._clip_slots:
            if clip_slot.will_record_on_start():
                will_record = True
        return will_record or self._main_clip_slot.is_recording
    
    def color(self):
        if self.has_clips():
            return self._main_clip_slot.color_index or 55
        else:
            return 'none'

    def is_playing(self):
        return self._main_clip_slot.is_playing

    def is_triggered(self):
        return self._main_clip_slot.is_triggered

    def is_recording(self):
        return self._main_clip_slot.is_recording

    def has_clips(self):
        for clip_slot in self._clip_slots:
            if clip_slot.has_clip():
                return True
        return False

    def display_first_clip(self):
        for clip_slot in self._clip_slots:
            if clip_slot.has_clip and not clip_slot._slot.clip.muted:
                self.module.set.base.song().view.detail_clip = clip_slot.clip
                self.module.set.base.canonical_parent.application().view.show_view('Detail/Clip')
                return


#Wrapper for clip_slot to add its track
class ClipSlot(EbiagiComponent):

    def __init__(self, slot, track, instrument=None, Set=None):
        super(ClipSlot, self).__init__()
        self._slot = slot
        self._track = track
        self._instrument = instrument
        self._set = Set
        self._held = False
        self._clip_commands = []
        if self._slot.has_clip:
            self.name = parse_clip_name(self._slot.clip.name)
            self._clip_commands = parse_clip_commands(self._slot.clip.name) or []
            self.log(self._clip_commands)

    #(because clip_slot.will_record_on_start does not work)
    def will_record_on_start(self):
        return not self._slot.has_clip and self._slot.has_stop_button and self._track.can_be_armed and self._track.arm

    def fire(self):
        # if self.will_record_on_start() and self._track.playing_slot_index > 0:
        #     if self._track.has_midi_input:
        #         self._slot.create_clip(1.0)
        #         self._slot.clip.name = 'CAN_CLEAR'
        #         self.deactivate_clip()
        #     return
        self._slot.fire()
        # if self.will_record_on_start() and not self._instrument.is_selected():
        #     return
        # else:
        #     self._slot.fire()

    def stop(self):
        if self._slot.has_clip:
            if list(self._track.clip_slots)[self._set.get_scene_index('STOPCLIP')].has_clip:
                list(self._track.clip_slots)[self._set.get_scene_index('STOPCLIP')].fire()
            else:
                for command in self._clip_commands:
                    if 'FA_BASE' in command:
                        self._track.stop_all_clips()
                self._slot.stop()

    def is_clearable(self):
        return self._slot.has_clip and 'CAN_CLEAR' in self._slot.clip.name or self._slot.is_recording

    def is_recording(self):
        return self._slot.is_recording

    def finish_record(self):
        self._slot.clip.name = 'CAN_CLEAR'
        self._slot.clip.legato = 1
        # if self._slot.clip.is_midi_clip:
        #     if is_empty_midi_clip(self._slot.clip):
        #         self.deactivate_clip()
        #         return False
        # if self._slot.clip.is_audio_clip:
        #     if not self._instrument.audio_in_armed():
        #         self.deactivate_clip()
        #         return False
        self._slot.fire()
        # self._slot.clip.add_playing_status_listener(partial(self.loop_clip,self._slot.clip))
        return True

    def loop_clip(self, clip):
        if not clip.is_recording:
            def woo():
                clip.loop_end = clip.length
                clip.loop_start = clip.length - 4.0
                clip.start_marker = clip.loop_start
            self.canonical_parent.schedule_message(0, woo)

    def is_group_clip(self):
        return self._slot.controls_other_clips

    def has_clip(self):
        return self._slot.has_clip

    def deactivate_clip(self):
        self._slot.clip.muted = 1
        self._slot.has_stop_button = 0

    def clear(self):
        if self._slot.has_clip:
            self._slot.delete_clip()
            self._slot.has_stop_button = 1

    def quantize(self):
        if self._slot.has_clip and self._slot.clip.is_midi_clip:
            self._slot.clip.quantize(5, 1.0)

    def run_select_commands(self):
        if self._slot.has_clip:

            self._held = True

            for command in self._clip_commands:

                if 'SELECT' in command:
                    self._set.select_instrument(None, self._instrument)
                    self._set.deselect_instrument(None, self._instrument)

                # if 'SNAP' in command:
                #     index = int(parse_clip_command_param(command))
                #     quantize = self._slot.clip.launch_quantization
                #     # if Global, use that quantize
                #     if quantize == 0:
                #         quantize = self._song.clip_trigger_quantization
                #     else:
                #         quantize -= 1
                #     # if None or less than a measure
                # if quantize == 0 or quantize >= 5:
                #     self._set.snap_control.select_snap(self._set.targetted_module.snaps[index])
                #     self._set.snap_control.ramp(0)
                # else:
                #     beat_divisors = {
                #         1: 8*self._song.signature_numerator,
                #         2: 4*self._song.signature_numerator,
                #         3: 2*self._song.signature_numerator,
                #         4: 1*self._song.signature_numerator,
                #     }
                #     beat_divisor = beat_divisors[quantize]
                #     total_beats = self._song.get_current_beats_song_time().beats + ((self._song.get_current_beats_song_time().bars - 1) * self._song.signature_numerator)
                #     if total_beats % beat_divisor == 0:
                #         self._set.snap_control.select_snap(self._set.targetted_module.snaps[index])
                #         self._set.snap_control.ramp(0)
                #     else:
                #         beats_remaining = beat_divisor - (total_beats % beat_divisor) - 1
                #         self._set.snap_control.schedule_snap(self._set.targetted_module.snaps[index], beats_remaining)

                if 'AUM' in command:
                    is_gradual = int(parse_clip_command_param(command))
                    quantize = self._slot.clip.launch_quantization
                    beats_remaining = 0
                    # if Global, use that quantize
                    if quantize == 0:
                        quantize = self._song.clip_trigger_quantization
                    else:
                        quantize -= 1
                    if quantize == 0 or quantize >= 5:
                        # self._set.snap_control.select_snap(self._set.targetted_module.snaps[index])
                        beats_remaining = 0
                    else:
                        beat_divisors = {
                            1: 8*self._song.signature_numerator,
                            2: 4*self._song.signature_numerator,
                            3: 2*self._song.signature_numerator,
                            4: 1*self._song.signature_numerator,
                        }
                        beat_divisor = beat_divisors[quantize]
                        total_beats = self._song.get_current_beats_song_time().beats + ((self._song.get_current_beats_song_time().bars - 1) * self._song.signature_numerator)
                        if total_beats % beat_divisor == 0:
                            beats_remaining = 0
                        else:
                            beats_remaining = beat_divisor - (total_beats % beat_divisor)

                    for param in self._instrument.get_instrument_device().parameters:
                        envelope = self._slot.clip.automation_envelope(param)
                        if envelope:
                            self._set.ramp_param(param, envelope.value_at_time(0.1), beats_remaining, is_gradual)

                if 'PQUANT' in command:
                    quantization = int(parse_clip_command_param(command))
                    if self._track.playing_slot_index >= 0:
                        self.trigger_clip_with_quantiaztion(self._slot.clip, quantization)
                    else:
                        self._slot.fire()

                if 'PLAY' in command:
                    clip_name_to_play = parse_clip_command_param(command)
                    for clip_slot in self._track.clip_slots:
                        if clip_slot.has_clip:
                            if parse_clip_name(clip_slot.clip.name) == clip_name_to_play:
                                self.trigger_clip_with_quantiaztion(clip_slot.clip, 0)
                                # clip_slot.fire()

                if 'STOP' in command:
                    self._track.stop_all_clips()

                if 'MUTE' in command:
                    self._instrument.mute_loops()

                if 'HOLD' in command:
                    self._slot.fire()

                if 'RETURN' in command:
                    self._slot.fire()

    
    def run_deselect_commands(self):
        if self._slot.has_clip:

            if self._clip_commands:
                for command in self._clip_commands:

                    if 'RETURN' in command:
                        for clip_slot in self._track.clip_slots:
                            if (clip_slot.is_playing or clip_slot.is_triggered) and clip_slot.clip != self._slot.clip and not self._slot.is_triggered:
                                return
                        params = parse_clip_command_param(command).split(',')
                        clip_name_to_play = params[0]
                        quantization = int(params[1])
                        for clip_slot in self._track.clip_slots:
                            if clip_slot.has_clip:
                                if parse_clip_name(clip_slot.clip.name) == clip_name_to_play:
                                    self.trigger_clip_with_quantiaztion(clip_slot.clip, quantization)

                    if 'HOLD' in command and self._held:
                        can_stop = True
                        for clip_slot in self._track.clip_slots:
                            if (clip_slot.is_playing or clip_slot.is_triggered) and clip_slot.clip != self._slot.clip:
                                can_stop = False
                        if can_stop:
                            list(self._track.clip_slots)[self._set.get_scene_index('STOPCLIP')].fire()

                    if 'MUTE' in command:
                        self._instrument.unmute_loops()         

            self._held = False


    def trigger_clip_with_quantiaztion(self, clip, quantization):
        return_quantization = math.floor(clip.launch_quantization)
        clip.launch_quantization = quantization
        self.midi_action(partial(self.finish_clip_trigger, clip, return_quantization))

    def finish_clip_trigger(self, clip, return_quantization):
        clip.fire()
        clip.launch_quantization = return_quantization

