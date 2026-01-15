from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Button, Static
from textual.screen import ModalScreen


class ConfirmationModal(ModalScreen[bool]):
    """
    A reusable confirmation modal.
    """

    BINDINGS = [
        Binding(
            "escape,n,q",
            "cancel",
            description="cancel",
            priority=True,
        ),
        Binding(
            "enter,y",
            "confirm",
            description="confirm",
            priority=True,
        ),
    ]

    def __init__(
        self,
        message: str,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.message_text = message

    def compose(self) -> ComposeResult:
        with VerticalScroll(classes="main") as container:
            container.border_title = "confirm"

            yield Static(
                self.message_text,
                id="message",
            )
            yield Horizontal(
                Button(
                    "(n)o",
                    variant="error",
                    id="cancel",
                ),
                Button(
                    "(y)es",
                    variant="success",
                    id="accept",
                ),
                classes="buttons",
            )

    def on_mount(self) -> None:
        self.query_one("#cancel").focus()

    def action_cancel(self) -> None:
        self.dismiss(False)

    def action_confirm(self) -> None:
        self.dismiss(True)

    @on(Button.Pressed)
    def handle_buttons(self, event: Button.Pressed) -> None:
        if event.button.id == "accept":
            self.dismiss(True)
        else:
            self.dismiss(False)
