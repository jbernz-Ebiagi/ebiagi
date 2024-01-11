from ._EbiagiComponent import EbiagiComponent
from ._naming_conventions import *
from _Framework.SubjectSlot import subject_slot
import Live

class Spine(EbiagiComponent):

    def __init__(self, track, Set, Module=None):
        super(Spine, self).__init__()
        self._track = track
        self._set = Set
        self._module = Module

        self.in_loop = None
        self.sections = []
        self.out_loop = None

        for clip in self._track.arrangement_clips:
            if parse_clip_name(clip.name):
                self.sections.append(Section(clip, self))

        self.triggered_section = None
        # self._scheduler = Live.Base.Timer(callback=self.on_tick, interval=1, repeat=True)

    def select_section(self, index):

        self.sections[index].play()
        # self.triggered_section = self.sections[index]
        # self._scheduler.start()

    # def on_tick(self):
    #     self.log(self._song.get_current_beats_song_time().ticks)
    #     imminent = self._song.get_current_beats_song_time().beats == 4 and self._song.get_current_beats_song_time().sub_division == 4 and self._song.get_current_beats_song_time().ticks >= 50
    #     new_measure = self._song.get_current_beats_song_time().beats == 1 and self._song.get_current_beats_song_time().sub_division == 1
    #     if imminent or new_measure:
    #         self._scheduler.stop()
    #         self.triggered_section.play()
    #         self.triggered_section = None

    def disconnect(self):
        super(Spine, self).disconnect()
        self._scheduler.stop()
        return

class Section(EbiagiComponent):
    def __init__(self, clip, Spine):
        super(Section, self).__init__()
        self.name = parse_clip_name(clip.name)
        self._spine = Spine
        self._clip = clip
        self._clip_commands = parse_clip_commands(clip.name) or []

        self.active = False

        # self.midi_action(self.create_cue_point)

        self._song.add_current_song_time_listener(self._on_song_time_changed)

    def _on_song_time_changed(self):
        is_playing = self._song.current_song_time >= self._clip.start_time and self._song.current_song_time < self._clip.end_time
        if is_playing and not self.active:
            self.midi_action(self.activate)
        elif not is_playing and self.active:
            self.midi_action(self.deactivate)

    def activate(self):
        if self._clip.looping:
            self._song.loop_start = self._clip.start_time + self._clip.loop_start
            self._song.loop_length = self._clip.length
            self._song.loop = True
        self.active = True
        if self._spine.triggered_section is self:
            self._spine.triggered_section = None
        self.log('activate section ' + self.name)

    def deactivate(self):
        self.active = False
        self.log('deactivate section ' + self.name)

    def play(self):
        self.log('play section ' + self.name)
        for cue in self._song.cue_points:
            if cue.time == self._clip.start_time:
                cue.jump()

    def color(self):
        return self._clip.color_index

    def create_cue_point(self):
        self.log('create cue')
        if not self._song.is_cue_point_selected():
            self.log('cue point')
            self._song.set_or_delete_cue()

    def disconnect(self):
        self._song.remove_current_song_time_listener(self._on_song_time_changed)
