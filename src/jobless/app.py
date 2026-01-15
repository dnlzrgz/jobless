from typing import Any

from sqlmodel import select
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.widgets import DataTable, Footer

from jobless.constants import APP_NAME
from jobless.db import get_engine, get_session, init_db
from jobless.models import Application, Company, Contact
from jobless.settings import Settings
from jobless.widgets.confirmation import ConfirmationModal
from jobless.widgets.header import AppHeader

TABLE_CONFIG = {
    "companies": {
        "model": Company,
        "columns": [
            "id",
            "name",
            "website",
            "industry",
        ],
        "to_row": lambda company: (
            str(company.id),
            company.name,
            company.website,
            company.industry,
        ),
    },
    "applications": {
        "model": Application,
        "columns": [
            "id",
            "title",
            "company",
            "status",
            "priority",
            "applied at",
            "last update at",
        ],
        "to_row": lambda application: (
            str(application.id),
            application.title,
            application.company.name,
            application.status,
            str(application.priority),
            application.date_applied.strftime("%Y-%m-%d")
            if application.date_applied
            else "N/A",
            application.follow_up_date.strftime("%Y-%m-%d")
            if application.follow_up_date
            else "N/A",
        ),
    },
    "contacts": {
        "model": Contact,
        "columns": [
            "id",
            "name",
            "email",
            "phone",
        ],
        "to_row": lambda contact: (
            str(contact.id),
            contact.name,
            contact.email,
            contact.phone,
        ),
    },
}


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
            "backspace",
            "delete",
            description="delete",
            tooltip="delete current entry",
        ),
        Binding(
            "R",
            "refresh_all",
            description="refresh all",
            tooltip="refresh the data",
        ),
    ]

    def __init__(self):
        super().__init__()

        self.settings: Settings = Settings()
        self.engine = get_engine(self.settings.db_url)

    def compose(self) -> ComposeResult:
        yield AppHeader()

        with ScrollableContainer(classes="main"):
            yield DataTable(
                id="companies",
                classes="table companies",
                zebra_stripes=True,
                cursor_type="row",
            )
            yield DataTable(
                id="applications",
                classes="table applications",
                zebra_stripes=True,
                cursor_type="row",
            )
            yield DataTable(
                id="contacts",
                classes="table contacts",
                zebra_stripes=True,
                cursor_type="row",
            )

        yield Footer()

    def on_mount(self) -> None:
        init_db(self.engine)

        self.theme = self.settings.theme
        for table_name, config in TABLE_CONFIG.items():
            table = self.query_one(f"#{table_name}", DataTable)
            assert table

            table.add_columns(*config["columns"])
            table.border_title = table_name
            self._load_data(table, config)

    def action_refresh_all(self) -> None:
        for table_name, config in TABLE_CONFIG.items():
            table = self.query_one(f"#{table_name}", DataTable)
            assert table

            self._load_data(table, config)

    def action_delete(self) -> None:
        focused = self.focused
        assert focused

        if isinstance(focused, DataTable) and focused.cursor_row is not None:
            table_id = focused.id
            assert focused.id

            item_id, item_name, *_ = focused.get_row_at(focused.cursor_row)

            def check_confirmation(confirmed: bool | None) -> None:
                if not confirmed:
                    return

                config = TABLE_CONFIG.get(table_id)
                assert config

                with get_session(self.engine) as session:
                    model = config["model"]
                    item = session.get(model, int(item_id))
                    if item:
                        session.delete(item)
                        session.commit()

                        self.notify(f'deleted "{item_name}" from {table_id}')
                        self.action_refresh_all()
                    else:
                        self.notify(f'item "{item_name}" not found', severity="error")

            self.push_screen(
                ConfirmationModal(
                    message=f'Are you sure you want to delete "{item_name}" from {table_id}?',
                ),
                callback=check_confirmation,
            )

    @work(thread=True)
    def _load_data(self, table: DataTable, config: dict) -> None:
        self.call_from_thread(setattr, table, "loading", True)

        with get_session(self.engine) as session:
            results = session.exec(select(config["model"])).all()
            rows = [config["to_row"](item) for item in results]

        self.call_from_thread(self._update_table_details, table, rows)

    def _update_table_details(self, table: DataTable, rows: list[Any]) -> None:
        table.clear()
        table.add_rows(rows)
        table.border_subtitle = f"{len(rows)}"
        table.loading = False


if __name__ == "__main__":
    app = JoblessApp()
    app.run()
