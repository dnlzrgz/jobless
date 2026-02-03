from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Static

from jobless.widgets.modals.base_form_modal import BaseFormModal


class ConfirmationModal(BaseFormModal[bool]):
    BINDINGS = [
        Binding(
            "y",
            "confirm",
            description="confirm",
            priority=True,
        ),
    ] + BaseFormModal.BINDINGS

    def __init__(self, message: str, *args, **kwargs) -> None:
        super().__init__(title="confirm", submit_label="confirm", *args, **kwargs)
        self.message = message

    def compose_form(self) -> ComposeResult:
        yield Static(self.message, id="message")

    def get_result(self) -> bool | None:
        return True

    def action_confirm(self) -> None:
        self.on_confirm()
