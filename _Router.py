from _EbiagiComponent import EbiagiComponent

class Router(EbiagiComponent):

    def __init__(self, track, Set):
        super(Router, self).__init__()
        self.track = track
        self.set = Set