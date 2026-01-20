from pydantic import ValidationError
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, TextArea

from jobless.models import Contact


class NewContactModal(ModalScreen[Contact]):
    """
    A modal for adding new contacts.
    """

    # TODO: pass list of company names
    # TODO: pass list of application names
    # TODO: add indicator for input status

    BINDINGS = [
        Binding(
            "escape",
            "cancel",
            description="cancel",
            priority=True,
        ),
    ]

    contact_name: reactive[str] = reactive("")

    def compose(self) -> ComposeResult:
        with VerticalScroll(classes="main form") as container:
            container.border_title = "new contact"
            self.name_input = Input(
                placeholder="john doe",
                type="text",
                id="name",
            )
            self.name_input.focus()

            self.email_input = Input(
                placeholder="john@doe.com",
                type="text",
                valid_empty=True,
                id="email",
            )
            self.phone_input = Input(
                placeholder="(555) 010-0001",
                type="text",
                valid_empty=True,
                id="phone",
            )
            self.url_input = Input(
                placeholder="johndoe.com",
                type="text",
                valid_empty=True,
                id="url",
            )
            self.notes_textarea = TextArea(
                placeholder="Anything that comes to mind.",
                id="notes",
            )

            yield Label("name")
            yield self.name_input

            yield Label("email")
            yield self.email_input

            yield Label("phone number")
            yield self.phone_input

            yield Label("url")
            yield self.url_input

            yield Label("notes")
            yield self.notes_textarea

            yield Horizontal(
                Button(
                    "cancel",
                    variant="error",
                    id="cancel",
                ),
                Button(
                    "add",
                    variant="success",
                    id="create",
                    disabled=True,
                ),
                classes="buttons",
            )

    def action_cancel(self) -> None:
        self.dismiss()

    @on(Input.Changed, "#name")
    def update_contact_name(self) -> None:
        self.contact_name = self.name_input.value.strip()

    def watch_contact_name(self) -> None:
        self.query_one("#create", Button).disabled = not self.name_input.value.strip()

    @on(Button.Pressed)
    def handle_buttons(self, event: Button.Pressed) -> None:
        if event.button.id == "create":
            self._submit_form()
        else:
            self.dismiss(None)

    def _submit_form(self) -> None:
        data = {
            "name": self.contact_name,
            "email": self.email_input.value or None,
            "phone": self.phone_input.value or None,
            "url": self.url_input.value or None,
            "notes": self.notes_textarea.text or None,
        }

        try:
            contact = Contact(**data)
            self.dismiss(contact)
        except ValidationError as e:
            for error in e.errors():
                field_name = error["loc"][0]
                message = error["msg"]

                self.app.notify(
                    f"invalid {field_name}: {message}",
                    title="validation error",
                    severity="error",
                )
        except Exception as e:
            self.app.notify(
                f"somethign went wrong: {e}",
                severity="error",
            )
