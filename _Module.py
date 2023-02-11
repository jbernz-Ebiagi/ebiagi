from ._EbiagiComponent import EbiagiComponent
from ._naming_conventions import *
from ._Instrument import Instrument
from ._Loop import Loop
from ._Snap import Snap
from ._utils import set_input_routing, set_output_routing


class Module(EbiagiComponent):

    def __init__(self, track, Set, m=0, a=0):
        super(Module, self).__init__()
        self._track = track
        self._set = Set
        self.instruments = []
        self.sends = []
        self.loops = {}

        self.short_name = get_short_name(track.name.split('.')[0])

        self._snap_data = self._track.get_data('snaps', False) or [[],[],[],[],[],[]]
        self.snaps = []

        self.log('Initializing Module %s...' % self.short_name)

        # set_output_routing(self._track, 'OUTPUT')

        i = list(self._song.tracks).index(track) + 1
        while not is_module(self._song.tracks[i].name) and self._song.tracks[i].is_grouped:

            #Add Instruments
            if is_instrument(self._song.tracks[i].name):
                instr = Instrument(self._song.tracks[i], Set, self)
                self.instruments.append(instr)

            if is_send(self._song.tracks[i].name):
                send_name = get_short_name(self._song.tracks[i].name.split('.')[1])
                set_input_routing(self._song.tracks[i], send_name+"-Return")
                self.sends.append(self._song.tracks[i])

            i += 1

        for instrument in self.instruments:
            instrument.pair_macros(self.instruments)

        for scene in self._song.scenes:
            if is_loop(scene.name):
                loop = Loop(track, scene, Set, self.instruments)
                self.loops[loop.short_name] = loop

        for snap in self._snap_data:
            self.snaps.append(Snap(snap, self, Set))

        self.clearCrossfade()

                
    def activate(self):
        self.log('Activating %s...' % self.short_name)
        for instrument in self.instruments:
            instrument.activate()
        for send in self.sends:
            send.current_monitoring_state = 0
        self._track.mute = 0
        # self._track.solo = 1

    def deactivate(self):
        self.log('Deactivating %s...' % self.short_name)
        for instrument in self.instruments:
            instrument.deactivate()
        for send in self.sends:
            send.current_monitoring_state = 2
        for loop in self.loops.values():
            loop.stop()
        self.fold()
        self._track.mute = 1
        # self._track.solo = 0
        self._track.mixer_device.volume.value = self._track.mixer_device.volume.min      

    def fold(self):
        self._track.fold_state = 1

    def unfold(self):
        self._track.fold_state = 0

    def assign_snap(self, index, param, track):
        for instrument in self.instruments:
            if instrument._track == track:
                if(param):
                    if not self.snaps[index].has_param(param):
                        self.snaps[index].create_param(instrument, param)
                        self.message('Added param %s to snap %s at %s' % (param.name, str(index+1), str(param.value)))
                    else:
                        self.snaps[index].remove_param(param)
                        self.message('Removed param %s from snap %s' % (param.name, str(index+1)))
                else:
                    i = 1
                    while i < 16:
                        if self.snaps[index].has_param(param):
                            self.snaps[index].remove_param(param)
                        self.snaps[index].create_param(instrument, instrument.get_instrument_device().parameters[i])
                        i += 1
                    self.message('Saved snap from %s to snap %s' % (instrument.short_name, str(index+1)))
                self._save_snaps()


    def clear_snap(self, index):
        self.snaps[index] = Snap([], self, self._set)
        self._save_snaps()
        self.message('Removed all params from snap %s' % str(index+1))

    def _save_snaps(self):
        data = []
        for snap in self.snaps:
            data.append(snap.get_data())
        self._track.set_data('snaps', data)
        self._snap_data = data

    def setCrossfadeA(self):
        self._track.mixer_device.crossfade_assign = 0
        for instr in self.instruments:
            instr._track.mixer_device.crossfade_assign = 0

    def setCrossfadeB(self):
        self._track.mixer_device.crossfade_assign = 2
        for instr in self.instruments:
            instr._track.mixer_device.crossfade_assign = 2

    def clearCrossfade(self):
        self._track.mixer_device.crossfade_assign = 1
        for instr in self.instruments:
            instr._track.mixer_device.crossfade_assign = 1

    def disconnect(self):
        super(Module, self).disconnect()
        for instrument in self.instruments:
            instrument.disconnect()