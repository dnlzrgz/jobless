from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Label, Static

from jobless.constants import APP_NAME, APP_VERSION


class AppHeader(Static):
    """
    Custom header of the app.
    """

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Label(APP_NAME, classes="title"),
            Label(APP_VERSION, classes="subtitle"),
            classes="header",
        )
