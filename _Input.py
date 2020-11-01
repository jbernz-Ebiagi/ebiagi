from _EbiagiComponent import EbiagiComponent
from _naming_conventions import *

class Input(EbiagiComponent):

    def __init__(self, track, Set):
        super(Input, self).__init__()
        self.track = track
        self.set = Set

        self.short_name = get_short_name(track.name)

        self.log('Initializing Input %s...' % self.short_name)

