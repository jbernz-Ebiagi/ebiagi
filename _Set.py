from _EbiagiComponent import EbiagiComponent
from _naming_conventions import *
from _Module import Module
from _Input import Input
from _Router import Router

class Set(EbiagiComponent):

    def __init__(self):
        super(Set, self).__init__()

        self.loading = True
        self.log('Loading Set...')

        self.inputs = {}

        self.midi_routers = []
        self.audio_routers = []
        
        self.modules = []
        self.active_module = None

        self.held_instruments = []

        for track in self._song.tracks:

            #Add inputs
            if is_input(track.name):
                ipt = Input(track, self)
                self.inputs[ipt.short_name] = ipt

            #Add midi routers       
            if is_midi_router(track.name):
                self.midi_routers.append(Router(track, self)) 
            
            #Add audio routers       
            if is_audio_router(track.name):
                self.audio_routers.append(Router(track, self)) 

        for track in self._song.tracks:

            #Add modules
            if is_module(track.name):
                module = Module(track, self)
                self.modules.append(module)
                module.deactivate()


        if len(self.modules):
            self.activate_module(0)
            self.loading = False
            self.message('Loaded Ebiagi Set')

    def activate_module(self, index):
        if self.modules[index]:
            if self.modules[index] != self.active_module:

                if self.active_module:
                    self.active_module.deactivate()

                self.modules[index].activate()
                self.active_module = self.modules[index]
            else:
                self.message('Module already active')
        else:
            self.log('Module index out of bounds')

    def select_instrument(self, index, instrument=None):
        if not instrument:
            instrument = self.active_module.instruments[index]
        self.held_instruments.append(instrument)
        instrument.select()
        self._update_routers()

    def deselect_instrument(self, index, instrument=None):
        if not instrument:
            instrument = self.active_module.instruments[index]       
        if instrument in self.held_instruments: 
            self.held_instruments.remove(instrument)
        instrument.deselect()
        self._update_routers()

    def select_loop(self, key):
        self.active_module.loops[key].select()

    def deselect_loop(self, key):
        self.active_module.loops[key].deselect()

    def stop_loop(self, key):
        self.active_module.loops[key].stop()

    def stop_all_loops(self):
        for loop in self.active_module.loops.values():
            loop.stop()

    def clear_loop(self, key):
        self.active_module.loops[key].clear()

    def toggle_metronome(self):
        self._song.metronome = not self._song.metronome

    def _update_routers(self):
        for ipt in self.inputs.values():
            if not ipt.empty():
                if ipt.has_midi_input:
                    for router in self.midi_routers:
                        router.update_input(ipt)
                if ipt.has_audio_input:
                    for router in self.audio_routers:
                        router.update_input(ipt)
