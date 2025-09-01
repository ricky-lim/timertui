from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Header, Footer

from timertui.timer_widget import Timer


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
