from typing import TypeVar

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button

from jobless.models import Base

T = TypeVar("T", bound=Base | bool)


class BaseFormModal(ModalScreen[T]):
    """
    Base class for all Jobless modals that act as a form.
    """

    BINDINGS = [
        Binding(
            "escape",
            "dismiss(None)",
            description="cancel",
            priority=True,
        ),
    ]

    def __init__(
        self,
        title: str,
        cancel_label: str = "cancel",
        submit_label: str = "save",
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.form_title = title
        self.cancel_label = cancel_label
        self.submit_label = submit_label

    def compose_form(self) -> ComposeResult:
        """
        Override to add specific inputs.
        """
        yield from []

    def get_result(self) -> T:
        """
        Override this to return data from the inputs.
        """
        raise NotImplementedError

    def compose(self) -> ComposeResult:
        with VerticalScroll(classes="form") as vs:
            vs.border_title = self.form_title
            yield from self.compose_form()

            yield Horizontal(
                Button(
                    self.cancel_label,
                    variant="error",
                    id="cancel",
                ),
                Button(
                    self.submit_label,
                    variant="success",
                    id="submit",
                ),
                classes="buttons",
            )

    @on(Button.Pressed, "#cancel")
    def on_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#submit")
    def on_confirm(self) -> None:
        self.dismiss(self.get_result())
