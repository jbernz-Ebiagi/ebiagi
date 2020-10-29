from _utils import catch_exception, set_output_routing, is_empty_clip, get_loop_key, on_same_row
from _Instrument import AudioInstrument
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from ClyphX_Pro.clyphx_pro.ClyphXComponentBase import ClyphXComponentBase, schedule, add_client, remove_client
from _Framework.SubjectSlot import subject_slot
from functools import partial
import Live, sys

class SnapFX(ControlSurfaceComponent):

    @catch_exception
    def __init__(self, track, Set, *a, **k):
        super(SnapFX, self).__init__(*a, **k)
        self.track = track
        self.set = Set
        self.snap_map = []
        self.selected_snap = None

        self.knob = self.track.devices[0].parameters[1]
        self.reset_knob = False

        self._on_macro_value_changed.subject = self.knob
        self._on_is_playing_changed.subject = self.set.base.song()

        self.last_beat = 0
        self.last_tick = 0
        self.ramping_params = []

        # add_client(self)

        self._scheduler = Live.Base.Timer(callback=self.on_tick, interval=1, repeat=True)

    def recall_snap(self, beats):
        if self.selected_snap:
            if beats == 0:
                self.switch(self.selected_snap)
            else:
                self.ramp(self.selected_snap, beats)
            self.set.message('Loading snap %s' % str(self.set.active_module.snaps.index(self.selected_snap)+1))


    def switch(self, snap):
        for snap_param in snap:

            if len(self.set.held_instruments) == 0 or next((x for x in self.set.held_instruments if x.track.name == snap_param['track_name']), None):

                #if the param is already ramping, stop that ramp
                for ramping_param in self.ramping_params:
                    if ramping_param['param'] == snap_param['param']:
                        self.ramping_params.remove(ramping_param)

                self._tasks.add(partial(self._update_parameter_value, snap_param['param'], snap_param['value']))

    def ramp(self, snap, num_beats):
        for snap_param in snap:

            if len(self.set.held_instruments) == 0 or next((x for x in self.set.held_instruments if x.track.name == snap_param['track_name']), None):
                
                #if the param is already ramping, stop that ramp
                for ramping_param in self.ramping_params:
                    if ramping_param['param'] == snap_param['param']:
                        self.ramping_params.remove(ramping_param)

                self.ramping_params.append({
                    'param': snap_param['param'],
                    'beats_remaining': num_beats,
                    'target_value': snap_param['value']
                })

    def select_snap(self, snap):
        self.track.arm = 1
        self.selected_snap = snap
        self._set_snap_map(snap)

    def deselect_snap(self):
        self.track.arm = 0

    def _set_snap_map(self, snap):
        self.snap_map = []
        self.knob.value = 0
        self.reset_knob = True
        for snap_param in snap:
            s = {
                'param': snap_param['param'],
                'starting_value': snap_param['param'].value,
                'diff': snap_param['value'] - snap_param['param'].value
            }
            self.snap_map.append(s)

    def assign_snap(self, snap, param, track):
        track_params = list(track.devices[0].parameters)

        if not param in track_params:
            self.message('Snaps params must be within a track\'s first device')
            return

        snap_param = {
            'param': param,
            'value': param.value,
            'track_name': track.name,
            'index': track_params.index(param)
        }
        for existing_param in snap:
            if existing_param['track_name'] == track.name and existing_param['index'] == track_params.index(param):
                self.set.active_module.snaps[index].remove(existing_param)
                self.message('Snap parameter %s removed' % param.name)
                self.set.active_module.save_snaps()
                return
        snap.append(snap_param)
        self.message('Snap parameter %s added at %s' % (param.name, param.value))
        self.set.active_module.save_snaps()


    @subject_slot('value')
    def _on_macro_value_changed(self):
        if self.reset_knob:
            self.reset_knob = False
            return
        for s in self.snap_map:
            new_value = s['starting_value'] + s['diff']*self.knob.value/self.knob.max
            self._tasks.add(partial(self._update_parameter_value, s['param'], new_value))

    @subject_slot('is_playing')
    def _on_is_playing_changed(self):
        if self.set.base.song().is_playing:
            self._scheduler.start()
        else:
            self._scheduler.stop()

    def on_tick(self):
        if len(self.ramping_params) > 0:
            self._do_ramp()
        self.last_beat = self.set.base.song().get_current_beats_song_time().beats
        self.last_subdivision = self.set.base.song().get_current_beats_song_time().sub_division
        self.last_tick = self.set.base.song().get_current_beats_song_time().ticks

    def _do_ramp(self):
        current_tick = self.set.base.song().get_current_beats_song_time().ticks
        tick_difference = float(current_tick - self.last_tick)
        if tick_difference < 0:
            tick_difference += 60

        for param in self.ramping_params:
            ticks_remaining = float(param['beats_remaining']*4*60 + (4 - self.last_subdivision)*60 + 60 - self.last_tick)
            if ticks_remaining <= 0:
                self._update_parameter_value(param['param'], param['target_value'])
                self.ramping_params.remove(param)
            else:
                value_difference = float(param['target_value'] - param['param'].value)
                new_value = tick_difference/ticks_remaining*value_difference + param['param'].value

                self._update_parameter_value(param['param'], new_value)

                if self.set.base.song().get_current_beats_song_time().beats != self.last_beat:
                    param['beats_remaining'] -= 1
            

    def disconnect(self):
        super(SnapFX, self).disconnect()
        #remove_client(self)
        self.ramping_params = []
        return


    @staticmethod
    def _update_parameter_value(param, value, _=None):
        if value > param.max:
            value = param.max
        elif value < param.min:
            value = param.min
        param.value = value

    def log(self, msg):
        self.set.log(msg)