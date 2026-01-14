from typing import Any
from sqlmodel import select
from textual import work
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import DataTable, Footer

from jobless.constants import APP_NAME
from jobless.db import get_engine, get_session, init_db
from jobless.models import Application, Company, Contact
from jobless.settings import Settings
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
