from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from ClyphX_Pro.clyphx_pro.ClyphXComponentBase import ClyphXComponentBase

class EbiagiComponent(ClyphXComponentBase):

    def __init__(self, *a, **k):
        super(EbiagiComponent, self).__init__(*a, **k)
        self._song = self.canonical_parent.song()

    def log(self, message):
        self.canonical_parent.log_message(message)

    def message(self, message):
        self.canonical_parent.show_message(message)

    