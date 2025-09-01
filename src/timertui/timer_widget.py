from textual.app import ComposeResult, on
from textual.containers import Vertical, Horizontal
from textual.widgets import Input, Button, Static, Digits
from textual.validation import Number, Length
from textual.reactive import reactive

from timertui.beeper import Beeper  # type: ignore


class Timer(Static):
    """Timer with name/time inputs and controls."""

    seconds: float = 0.0
    name: str = ""
    initialized: bool = True

    def compose(self) -> ComposeResult:
        with Vertical(id="inputs"):
            yield Static("Name", id="label_name")
            yield Input(
                placeholder="Set timer name",
                id="name_input",
                validators=[Length(1, 50)],
            )
            yield Static("Time (seconds)", id="label_time")
            yield Input(
                placeholder="Set timer in seconds",
                id="time_input",
                validators=[Number(1, 3600)],
            )
        with Horizontal(id="controls"):
            yield Button("Start", id="start", variant="success")
            yield Button("Stop", id="stop", variant="error")
            yield Button("Reset", id="reset", variant="warning")
            yield TimeDisplay("00:00:00.00", id="time_display", beep=Beeper())

    @on(Input.Changed, "#time_input")
    def update_time_value(self, event: Input.Changed) -> None:
        try:
            self.seconds = float(event.value or 0)
        except ValueError:
            pass

    @on(Input.Changed, "#name_input")
    def update_name(self, event: Input.Changed) -> None:
        self.name = event.value or ""

    @on(Button.Pressed, "#start")
    @on(Input.Submitted, "#time_input")
    def start_timer(self) -> None:
        name_value = self.query_one("#name_input", Input).value or ""
        time_value = self.query_one("#time_input", Input).value or ""
        time_display = self.query_one("#time_display", TimeDisplay)

        if self.initialized or time_display.remaining_time == 0:
            if not time_value.isdigit():
                return self.notify("Enter valid seconds (1–3600)", severity="error")

            self.seconds = float(time_value)
            self.name = name_value
            self.initialized = False
            self.add_class("started")
            time_display.remaining_time = self.seconds
            time_display.name = self.name
            time_display.start()
        else:
            self.add_class("started")
            time_display.start()

    @on(Button.Pressed, "#stop")
    def stop_timer(self) -> None:
        self.remove_class("started")
        self.query_one("#time_display", TimeDisplay).stop()

    @on(Button.Pressed, "#reset")
    def reset_timer(self) -> None:
        self.remove_class("started")
        self.initialized = True
        display = self.query_one("#time_display", TimeDisplay)
        display.remaining_time = self.seconds
        display.reset()


class TimeDisplay(Digits):
    """Countdown display with beep on finish."""

    remaining_time: float = reactive(0.0)  # type: ignore
    just_resumed: bool = False
    name: str = ""

    def __init__(self, *args, beep=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.beep = beep

    def watch_remaining_time(self) -> None:
        time = self.remaining_time
        time, seconds = divmod(time, 60)
        hours, minutes = divmod(time, 60)
        time_string = f"{hours:02.0f}:{minutes:02.0f}:{seconds:05.2f}"
        self.update(time_string)

    def on_mount(self) -> None:
        self._timer = self.set_interval(1 / 60, self.update_remaining_time, pause=True)

    def update_remaining_time(self) -> None:
        if self.just_resumed:
            self.just_resumed = False
        elif self.remaining_time > 0:
            self.remaining_time = max(0, self.remaining_time - 1 / 60)
        else:
            self._timer.pause()
            self.notify(f"Timer '{self.name}' finished!", severity="error")
            self.update("Finished!")
            self.beep.start()

    def start(self) -> None:
        self.just_resumed = True
        self._timer.resume()

    def stop(self) -> None:
        self._timer.pause()
        self.beep.stop()

    def reset(self) -> None:
        self._timer.pause()
        self.beep.stop()
