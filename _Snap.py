from ._EbiagiComponent import EbiagiComponent
from ._naming_conventions import *

class Snap(EbiagiComponent):

    def __init__(self, data, Module, Set):
        super(Snap, self).__init__()
        self._set = Set

        self.snap_params = []
        self.ramping_params = []

        for d in data:
            for instrument in Module.instruments:
                if d['instr_name'] == get_short_name(instrument._track.name):
                    self.snap_params.append(SnapParam(instrument, instrument._track.devices[0].parameters[d['param_index']], d['param_value']))
        
        self.log(self.snap_params)


    def create_param(self, instrument, param):
        self.snap_params.append(SnapParam(instrument, param, param.value))

    def remove_param(self, param):
        for snap_param in self.snap_params:
            if snap_param.param == param:
                self.snap_params.remove(snap_param)

    def has_param(self, param):
        for snap_param in self.snap_params:
            if snap_param.param == param:
                return True
        else:
            return False

    def get_data(self):
        data = []
        for snap_param in self.snap_params:
            data.append(snap_param.get_data())
        return data


class SnapParam:

    def __init__(self, instrument, param, value):
        self.instrument = instrument
        self.param = param
        self.value = value

    def get_data(self):
        return {
            "instr_name": get_short_name(self.instrument._track.name),
            "param_index": list(self.instrument._track.devices[0].parameters).index(self.param),
            "param_value": self.value
        }


