import simpleaudio as sa

class Alarm:
    def __init__(self, file_path):
        self._wave_obj = sa.WaveObject.from_wave_file(file_path)
        self._play_obj = None

    def is_playing(self):
        return self._play_obj and self._play_obj.is_playing()

    def stop(self):
        if self._play_obj and self._play_obj.is_playing():
            self._play_obj.stop()

    def play(self):
        if not self._play_obj or not self._play_obj.is_playing():
            self._play_obj = self._wave_obj.play()
