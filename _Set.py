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

        self.inputs = []

        self.midi_routers = []
        self.audio_routers = []
        
        self.modules = []
        self.active_module = None

        for track in self._song.tracks:

            #Add inputs
            if is_input(track.name):
                self.inputs.append(Input(track, self))

            #Add midi routers       
            if is_midi_router(track.name):
                self.midi_routers.append(Router(track, self)) 
            
            #Add audio routers       
            if is_audio_router(track.name):
                self.audio_routers.append(Router(track, self)) 

        for track in self._song.tracks:

            #Add modules
            if is_module(track.name):
                self.modules.append(Module(track, self))

        if len(self.modules):
            self.active_module = self.modules[0]
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

    def select_instrument(self, index):
        self.active_module.instruments[index].select()

    def toggle_metronome(self):
        self._song.metronome = not self._song.metronome
