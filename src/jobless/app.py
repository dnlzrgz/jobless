from sqlmodel import select
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.widgets import Footer

from jobless.constants import APP_NAME
from jobless.db import get_engine, get_session, init_db
from jobless.settings import Settings
from jobless.widgets.confirmation import ConfirmationModal
from jobless.widgets.datatables import (
    ApplicationTable,
    CompanyTable,
    ContactTable,
    JoblessTable,
)
from jobless.widgets.header import AppHeader


class JoblessApp(App):
    """
    A Textual-based job tracking application.
    """

    TITLE = APP_NAME
    CSS_PATH = "global.tcss"
    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [
        Binding(
            "ctrl+c",
            "app.quit",
            description="quit",
            tooltip="quit the application",
            priority=True,
        ),
        Binding(
            "R",
            "reload",
            description="reload",
            tooltip="reload all tables",
        ),
    ]

    def __init__(self):
        super().__init__()

        self.settings: Settings = Settings()
        self.engine = get_engine(self.settings.db_url)

    def compose(self) -> ComposeResult:
        yield AppHeader()

        with ScrollableContainer(classes="main"):
            self.company_table = CompanyTable(
                id="companies",
                classes="table companies",
            )
            yield self.company_table

            self.application_table = ApplicationTable(
                id="applications",
                classes="table applications",
            )
            yield self.application_table

            self.contact_table = ContactTable(
                id="contacts",
                classes="table contacts",
            )
            yield self.contact_table

        yield Footer()

    def on_mount(self) -> None:
        init_db(self.engine)

        self.theme = self.settings.theme
        self.reload_tables()

    def action_reload(self) -> None:
        self.reload_tables()

    @on(JoblessTable.Delete)
    def delete_item(self, message: JoblessTable.Delete) -> None:
        def check_confirmation(confirmed: bool | None) -> None:
            if not confirmed:
                return

            with get_session(self.engine) as session:
                model = message.sender.MODEL
                instance = session.exec(
                    select(model).where(model.id == message.item_id)
                ).first()
                if not instance:
                    self.notify(
                        f'error finding item "{message.item_name}" in {message.sender.id}',
                        severity="error",
                    )
                    return

                session.delete(instance)
                session.commit()

                self.notify(f'deleted "{message.item_name}" from {message.sender.id}')

            self.reload_tables()

        self.push_screen(
            ConfirmationModal(
                message=f'delete "{message.item_name}" from {message.sender.id}?'
            ),
            callback=check_confirmation,
        )

    @work(thread=True, exclusive=True)
    def reload_tables(self) -> None:
        tables = [self.application_table, self.company_table, self.contact_table]
        for table in tables:
            self.call_from_thread(setattr, table, "loading", True)

        with get_session(self.engine) as session:
            for table in tables:
                results = session.exec(select(table.MODEL)).all()
                rows = [table.item_to_row(item) for item in results]

                self.call_from_thread(table.reload, rows)


if __name__ == "__main__":
    app = JoblessApp()
    app.run()
