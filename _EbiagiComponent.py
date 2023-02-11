from _Framework.ControlSurfaceComponent import ControlSurfaceComponent

class EbiagiComponent(ControlSurfaceComponent):

    def __init__(self, *a, **k):
        super(EbiagiComponent, self).__init__(*a, **k)
        self._song = self.canonical_parent.song()

    def log(self, message):
        self.canonical_parent.log_message(message)

    def message(self, message):
        self.canonical_parent.show_message(message)

    def midi_action(self, action, priority=False):
        self.canonical_parent.trigger_midi_action(action, priority)