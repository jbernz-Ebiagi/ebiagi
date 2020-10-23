from _utils import catch_exception, set_output_routing, is_empty_clip, get_loop_key, on_same_row
from _Instrument import AudioInstrument
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from ClyphX_Pro.clyphx_pro.ClyphXComponentBase import ClyphXComponentBase
from _Framework.SubjectSlot import subject_slot
from functools import partial

class SnapFX(ControlSurfaceComponent):

    @catch_exception
    def __init__(self, track, Set, *a, **k):
        super(SnapFX, self).__init__(*a, **k)
        self.track = track
        self.set = Set
        self.snap_map = []

        self.knob = self.track.devices[0].parameters[1]
        self.reset_knob = False

        self._on_macro_value_changed.subject = self.knob

    def set_snap_map(self, snap):
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

    @subject_slot('value')
    def _on_macro_value_changed(self):
        if self.reset_knob:
            self.reset_knob = False
            return
        for s in self.snap_map:
            new_value = s['starting_value'] + s['diff']*self.knob.value/self.knob.max
            self.log(s['param'].name)
            self.log(s['diff'])
            self.log(s['starting_value'])
            self._tasks.add(partial(self._update_parameter_value, s['param'], new_value))

    @staticmethod
    def _update_parameter_value(param, value, _=None):
        if value > param.max:
            value = param.max
        elif value < param.min:
            value = param.min
        param.value = value

    def log(self, msg):
        self.set.log(msg)