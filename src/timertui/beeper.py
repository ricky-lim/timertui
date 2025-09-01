import threading
import sys
import shutil
import subprocess
from pathlib import Path
import wave

try:
    import pyaudio
except ImportError:
    pyaudio = None


class Beeper:
    """Play a repeating beep in a background thread."""

    def __init__(self, wav_filename="beep.wav", interval=1.0):
        self.wav_path = Path(__file__).parent / wav_filename
        self.interval = interval
        self._stop = threading.Event()
        self._thread = None

    def _run(self):
        while not self._stop.wait(self.interval):
            _play_wav(self.wav_path)

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None


def _play_wav(path: Path):
    """Play a WAV file, preferring macOS afplay, then PyAudio, then terminal bell."""
    if sys.platform.startswith("darwin") and shutil.which("afplay"):
        subprocess.run(["afplay", str(path)], check=False)
        return

    if pyaudio:
        wf = wave.open(path, "rb")
        player = pyaudio.PyAudio()
        try:
            stream = player.open(
                format=player.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
            )
            for chunk in iter(lambda: wf.readframes(1024), b""):
                stream.write(chunk)
            stream.stop_stream()
            stream.close()
        finally:
            wf.close()
            player.terminate()
        return

    # Fallback: terminal bell
    print("\a", end="", flush=True)
