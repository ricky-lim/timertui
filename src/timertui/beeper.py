import threading
import sys
import shutil
import subprocess
from pathlib import Path


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
    """Play a WAV file, preferring macOS afplay, WSL paplay, then PyAudio, then terminal bell."""
    path_str = str(path)
    
    # macOS: Use afplay
    if sys.platform.startswith("darwin") and shutil.which("afplay"):
        subprocess.run(["afplay", path_str], check=False)
        return

    # WSL: Use paplay (PulseAudio)
    if _is_wsl() and shutil.which("paplay"):
        subprocess.run(["paplay", path_str], check=False, stderr=subprocess.DEVNULL)
        return

    # Fallback: terminal bell
    print("\a", end="", flush=True)

def _is_wsl():
    """Check if running in Windows Subsystem for Linux."""
    try:
        with open('/proc/version', 'r') as f:
            return 'microsoft' in f.read().lower() or 'wsl' in f.read().lower()
    except (FileNotFoundError, PermissionError):
        return False

