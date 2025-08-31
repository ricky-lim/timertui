from pathlib import Path

from textual.app import App, ComposeResult
from textual import on
from textual.containers import ScrollableContainer, Vertical, Horizontal
from textual.widgets import Header, Footer, Input, Button, Static, Digits
from textual.validation import Number, Length
from textual.reactive import reactive


class TimeDisplay(Digits):
    remaining_time = reactive(0.0)
    # Keep track of whether the timer is paused/resumed
    just_resumed = False
    name = ""

    def watch_remaining_time(self):
        time = self.remaining_time
        time, seconds = divmod(time, 60)
        hours, minutes = divmod(time, 60)
        time_string = f"{hours:02.0f}:{minutes:02.0f}:{seconds:05.2f}"
        self.update(time_string)

    def on_mount(self) -> None:
        self.update_timer = self.set_interval(
            1 / 60, self.update_remaining_time, pause=True
        )

    def update_remaining_time(self):
        if self.just_resumed:
            self.just_resumed = False
            return
        if self.remaining_time > 0.0 and not self.just_resumed:
            self.remaining_time = max(0.0, self.remaining_time - (1 / 60))
        if self.remaining_time == 0.0:
            self.stop()
            self.notify(f"Timer for {self.name} finished!", severity="info")

    def start(self):
        self.just_resumed = True
        self.update_timer.resume()

    def stop(self):
        self.update_timer.pause()

    def reset(self):
        self.update_timer.pause()


class Timer(Static):

    initialized = True
    seconds = 0.0
    name = ""

    def compose(self) -> ComposeResult:
        with Vertical(id="inputs"):
            yield Static("Name", id="label_name")
            yield Input(
                placeholder="Set timer name",
                id="name_input",
                validators=[Length(minimum=1, maximum=50)],
            )
            yield Static("Time (seconds)", id="label_time")
            yield Input(
                placeholder="Set timer in seconds",
                id="time_input",
                validators=[Number(minimum=1, maximum=3600)],
            )
        with Horizontal(id="controls"):
            yield Button("Start", id="start", variant="success")
            yield Button("Stop", id="stop", variant="error")
            yield Button("Reset", id="reset", variant="warning")
            yield TimeDisplay("00:00:00.00", id="time_display")

    @on(Input.Changed, "#time_input")
    def update_time_value(self, event: Input.Changed) -> None:
        if event.value:
            try:
                self.seconds = float(event.value)
            except:
                pass

    @on(Input.Changed, "#name_input")
    def update_name(self, event: Input.Changed) -> None:
        if event.value:
            self.name = event.value

    @on(Button.Pressed, "#start")
    @on(Input.Submitted, "#time_input")
    def start_timer(self):
        name_value = self.query_one("#name_input", Input).value
        time_value = self.query_one("#time_input", Input).value
        time_display = self.query_one("#time_display", TimeDisplay)

        if self.initialized or time_display.remaining_time == 0.0:
            self.init_timer(name_value, time_value)
        else:
            self.add_class("started")
            time_display.start()

    def init_timer(self, name_value: str, time_value: str) -> None:
        if (
            not time_value
            or not time_value.isdigit()
            or not (1 <= int(time_value) <= 3600)
        ):
            self.notify(
                "Please enter a valid time in seconds (1-3600)", severity="error"
            )
            return

        if self.initialized:
            self.add_class("started")
            self.initialized = False

        self.seconds = float(time_value)
        self.name = name_value

        time_display = self.query_one("#time_display", TimeDisplay)
        time_display.remaining_time = self.seconds
        time_display.name = self.name
        time_display.start()

    @on(Button.Pressed, "#stop")
    def stop_timer(self) -> None:
        self.remove_class("started")
        time_display = self.query_one("#time_display", TimeDisplay)
        time_display.stop()

    @on(Button.Pressed, "#reset")
    def reset_timer(self) -> None:
        self.remove_class("started")
        self.initialized = True
        time_display = self.query_one("#time_display", TimeDisplay)
        time_display.remaining_time = self.seconds
        time_display.reset()


class TimerApp(App):
    BINDINGS = [
        ("ctrl+d", "toggle_dark", "Toggle dark mode"),
        ("ctrl+q", "quit", "Quit the application"),
        ("ctrl+a", "add_timer", "Add a new timer"),
        ("ctrl+r", "remove_timer", "Remove the last timer"),
    ]

    CSS_PATH = Path(__file__).parent / "timer.tcss"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        with ScrollableContainer(id="timers"):
            yield Timer()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_add_timer(self) -> None:
        """Add a new timer."""
        timer = Timer()
        self.query_one("#timers").mount(timer)
        timer.scroll_visible()

    def action_remove_timer(self) -> None:
        """Remove the last timer."""
        timers = self.query(Timer)
        if timers:
            timers.last().remove()


def main():
    TimerApp().run()


if __name__ == "__main__":
    main()
