from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer


class AudioPlayer:
    def __init__(self):
        self._player = QMediaPlayer()
        self._audio_output = QAudioOutput()
        self._player.setAudioOutput(self._audio_output)

    def play(self, file_path: str):
        self._player.setSource(file_path)
        self._player.play()

    def stop(self):
        self._player.stop()

    def set_volume(self, volume: float):
        self._audio_output.setVolume(volume)
