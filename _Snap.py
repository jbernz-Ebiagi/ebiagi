from ._EbiagiComponent import EbiagiComponent
from ._naming_conventions import *

class Snap(EbiagiComponent):

    def __init__(self, data, Module, Set):
        super(Snap, self).__init__()
        self._set = Set

        self.snap_params = []
        self.ramping_params = []

        self.log('load snap')
        self.log(data)

        for d in data:
            for instrument in Module.instruments:
                if d['instr_name'] == get_short_name(instrument._track.name):
                    try:
                        self.snap_params.append(SnapParam(instrument, parse_param_index(d['param_index'], instrument.get_instrument_device()), d['param_value']))
                    except:
                        self.log('could not load snap')

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
        self.log('get snap data')
        self.log(data)
        return data


class SnapParam:

    def __init__(self, instrument, param, value):
        self.instrument = instrument
        self.param = param
        self.value = value

    def get_data(self):
        return {
            "instr_name": get_short_name(self.instrument._track.name),
            "param_index": get_param_index(self.param, self.instrument.get_instrument_device()),
            "param_value": self.value
        }

#recursively search for a param in a device and return a compound index
def get_param_index(param, device):
    childDeviceIndex = 0
    chainIndex = 0
    paramIndex = 0
    for parameter in device.parameters:
        if param == parameter:
            return paramIndex
        paramIndex += 1
    if device.can_have_chains:
        for chain in device.chains:
            childDeviceIndex = 0
            for childDevice in chain.devices:
                n = get_param_index(param, childDevice)
                if n:
                    return [chainIndex, childDeviceIndex, n]
                childDeviceIndex += 1
            chainIndex += 1
    return False

def parse_param_index(paramIndex, device):
    if isinstance(paramIndex, list):
        return parse_param_index(paramIndex[2], device.chains[paramIndex[0]].devices[paramIndex[1]])
    else:
        return device.parameters[paramIndex]





