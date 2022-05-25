from ._Instrument import Instrument
from ._naming_conventions import *
from ._utils import catch_exception
from _Framework.SubjectSlot import subject_slot
from functools import partial
import Live

class SnapControl(Instrument):

    def __init__(self, track, Set):
        super(SnapControl, self).__init__(track, Set)
        self._track = track
        self._set = Set

        self._snap_map = []
        self.selected_snap = None

        self._knob = self.get_instrument_device().parameters[1]
        self._reset_knob = False

        self._on_macro_value_changed.subject = self._knob

        self._last_beat = 0
        self._last_subdivision = 0
        self._last_tick = 0
        self._ramping_params = []

        self._scheduler = Live.Base.Timer(callback=self.on_tick, interval=1, repeat=True)
        self._scheduler.start()

    def select_snap(self, snap):
        self._reset_knob = True
        self.selected_snap = snap
        self._set_snap_map(snap)
        self._reset_knob = False

    def _set_snap_map(self, snap):
        self._snap_map = []
        self._knob.value = 0
        for snap_param in snap.snap_params:
            s = {
                'param': snap_param.param,
                'starting_value': snap_param.param.value,
                'diff': snap_param.value - snap_param.param.value
            }
            self._snap_map.append(s)

    @subject_slot('value')
    def _on_macro_value_changed(self):
        self.log(self._knob.value)
        if self._reset_knob:
            return
        for s in self._snap_map:
            new_value = s['starting_value'] + s['diff']*self._knob.value/self._knob.max
            self._tasks.add(partial(self._update_parameter_value, s['param'], new_value))

    def ramp(self, num_beats):

        for snap_param in self.selected_snap.snap_params:

            if len(self._set.held_instruments) == 0 or (len(self._set.held_instruments) == 1 and self in self._set.held_instruments) or next((x for x in self._set.held_instruments if x == snap_param.instrument), None):

                #if the param is already ramping, stop that ramp
                for ramping_param in self._ramping_params:
                    if ramping_param['param'] == snap_param.param:
                        self._ramping_params.remove(ramping_param)

                if not self._song.is_playing:
                    snap_param.param.value = snap_param.value
                    return

                self._ramping_params.append({
                    'param': snap_param.param,
                    'beats_remaining': num_beats,
                    'target_value': snap_param.value
                })

    @catch_exception
    def on_tick(self):
        if len(self._ramping_params) > 0:
            self._do_ramp()
        self._last_beat = self._song.get_current_beats_song_time().beats
        self._last_subdivision = self._song.get_current_beats_song_time().sub_division
        self._last_tick = self._song.get_current_beats_song_time().ticks

    @catch_exception
    def _do_ramp(self):
        current_tick = self._song.get_current_beats_song_time().ticks
        tick_difference = float(current_tick - self._last_tick)

        if tick_difference < 0:
            tick_difference += 60

        for param in self._ramping_params:
            ticks_remaining = float(param['beats_remaining']*4*60 + (4 - self._last_subdivision)*60 + 60 - self._last_tick)
            if ticks_remaining <= 0:
                self._update_parameter_value(param['param'], param['target_value'])
                self._ramping_params.remove(param)
            else:
                value_difference = float(param['target_value'] - param['param'].value)
                new_value = tick_difference/ticks_remaining*value_difference + param['param'].value

                self._update_parameter_value(param['param'], new_value)

                if self._song.get_current_beats_song_time().beats != self._last_beat:
                    param['beats_remaining'] -= 1
            

    def disconnect(self):
        super(SnapControl, self).disconnect()
        self._scheduler.stop()
        self.ramping_params = []
        return

    @staticmethod
    def _update_parameter_value(param, value, _=None):
        if value > param.max:
            value = param.max
        elif value < param.min:
            value = param.min
        param.value = value