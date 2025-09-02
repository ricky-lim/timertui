# TimerTUI

A beautiful terminal timer app built with [Textual](https://www.textualize.io/). Supports multiple independent timers, each with its own sound.

## Features

- Add, remove, and run multiple timers in parallel
- Each timer has its own independent beep (plays `beep.wav` on finish)
- Modern TUI interface with dark/light mode toggle
- Keyboard shortcuts for developer ergonomics

## Run 

For WSL, `pulseaudio` is needed for the beeping sound. 
You can install with: `sudo apt install pulseaudio`

```
uvx 'git+https://github.com/ricky-lim/timertui.git'
```

https://github.com/user-attachments/assets/ed19e408-b7e3-4a1c-9206-9d97c250969c


## Installation

1. **Clone the repository:**
	```sh
	git clone https://github.com/ricky-lim/timertui.git
	cd timertui
	```
2. **Create and activate a Python 3.13+ virtual environment:**
	```sh
    uv venv --python 3.13 --seed
	source .venv/bin/activate
	```
3. **Install dependencies:**
	```sh
    uv sync
    # Install for development
	pip install -e .
	```

## Usage

Run the timer TUI:

```sh
timertui
```

### Keyboard Shortcuts

- `Ctrl+A` — Add a new timer
- `Ctrl+R` — Remove the last timer
- `Ctrl+D` — Toggle dark/light mode
- `Ctrl+Q` — Quit the app

### Timer Controls

- Set a name and duration (in seconds) for each timer
- Start, stop, and reset timers independently
- Each timer will play its own `beep.wav` sound continuously until you reset

## Sound Requirements

- The app uses `beep.wav` (in `src/timertui/`) for timer sounds
- On macOS, the app uses the system `afplay` for playback (no PyAudio needed)
- On other platforms, [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/) is required

## Development

To run in development mode with hot reload:

```sh
textual run --dev src/timertui/main.py
```

## License

MIT License. See [LICENSE](LICENSE) for details.
