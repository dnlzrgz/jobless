from typing import TypeVar

from pydantic import ValidationError
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.css.query import NoMatches
from textual.screen import ModalScreen
from textual.widgets import Button, Input

from jobless.schemas import BaseSchema

T = TypeVar("T", bound=BaseSchema | bool)


class FormModal(ModalScreen[T]):
    """
    Base class for all Jobless modals that act as a form.
    """

    BINDINGS = [
        Binding(
            "escape",
            "dismiss(None)",
            description="cancel",
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

    def get_result(self) -> T | None:
        """
        Override this to return data from the inputs.
        """
        raise NotImplementedError

    def notify_validation_errors(self, e: ValidationError) -> None:
        for error in e.errors():
            field = error["loc"][0]
            msg = error["msg"]
            self.notify(
                f"{field}: {msg}",
                severity="error",
                title="validatin error",
            )

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

    def on_mount(self) -> None:
        try:
            first_input = self.query(Input).first()
            first_input.focus()
        except NoMatches:
            return

    @on(Button.Pressed, "#cancel")
    def on_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#submit")
    def on_confirm(self) -> None:
        result = self.get_result()
        if result:
            self.dismiss(result)


class EditFormModal(FormModal[T]):
    def __init__(
        self,
        title: str,
        instance: T,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(title=title, *args, **kwargs)
        self.instance = instance

    def get_result(self) -> T | None:
        raise NotImplementedError

    def load_data(self) -> None:
        """
        Override this in subclass to map self.instance attributes
        to the widgets values.
        """
        raise NotImplementedError()

    def on_mount(self) -> None:
        super().on_mount()
        self.load_data()
