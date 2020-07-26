from _utils import catch_exception

class Input:

    @catch_exception
    def __init__(self, track, set):
        self.set = set
        self.track = track
        self.midi_inputs = []
        self.audio_inputs = []

        tracks = self.set.tracks
        i = tracks.index(track) + 1
        while tracks[i].is_grouped:
            if tracks[i].is_midi_track:
                midi_inputs.append(tracks[i])
            else if tracks[i].is_audio_track:
                audio_inputs.append(tracks[i])
            i += 1


    def log(self, msg):
        self.set.log(msg)