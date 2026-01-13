from typing import Any, Callable
from sqlmodel import select
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, ScrollableContainer
from textual.widgets import DataTable, Footer, Label, Static

from jobless.constants import APP_NAME, APP_VERSION
from jobless.db import get_engine, get_session, init_db
from jobless.models import Application, Company, Contact
from jobless.settings import Settings


class CustomHeader(Static):
    def __init__(self, title: str, subtitle: str) -> None:
        self.title = title
        self.subtitle = subtitle
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Label(self.title, classes="title"),
            Label(self.subtitle, classes="subtitle"),
            classes="header",
        )


class CustomDataTable(DataTable):
    def __init__(
        self,
        label: str,
        cursor_type: str = "row",
        **kwargs,
    ) -> None:
        super().__init__(id=label, classes=label, **kwargs)
        self.border_title = label
        self.cursor_type = cursor_type
        self.zebra_stripes = True

    @work(thread=True)
    def update_data(self, engine: Any, model: Any, row_factory: Callable) -> None:
        self.app.call_from_thread(setattr, self, "loading", True)

        with get_session(engine) as session:
            statemet = select(model)
            results = session.exec(statemet).all()

            rows = [(str(item.id), row_factory(item)) for item in results]

            self.app.call_from_thread(self._refresh_data, rows)

    def _refresh_data(self, rows: list[tuple[str, list]]) -> None:
        self.clear()

        for row_id, row_data in rows:
            self.add_row(*row_data, key=row_id)

        self.loading = False
        self.border_subtitle = f"{len(rows)} items"


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
        self.custom_header: Static = CustomHeader(f"↪ {APP_NAME}", f"{APP_VERSION}")
        self.applications_table = CustomDataTable("applications")
        self.companies_table: DataTable = CustomDataTable("companies")
        self.contacts_table: DataTable = CustomDataTable("contacts")

        yield self.custom_header

        with ScrollableContainer(classes="main"):
            yield self.companies_table
            yield self.applications_table
            yield self.contacts_table

        yield Footer()

    def on_mount(self) -> None:
        init_db(self.engine)

        self.theme = self.settings.theme
        self._setup_and_load_tables()

    def _setup_and_load_tables(self) -> None:
        self.applications_table.add_columns(
            "id",
            "title",
            "company",
            "status",
            "priority",
        )
        self.applications_table.update_data(
            self.engine,
            Application,
            lambda a: (str(a.id), a.title, a.company.name, a.status, a.priority),
        )

        self.companies_table.add_columns(
            "id",
            "name",
            "website",
            "industry",
            "applications",
            "skills",
            "contacts",
        )
        self.companies_table.update_data(
            self.engine,
            Company,
            lambda c: (
                str(c.id),
                c.name,
                c.website,
                c.industry,
                str(len(c.applications)),
                str(len(c.skills)),
                str(len(c.contacts)),
            ),
        )

        self.contacts_table.add_columns(
            "id",
            "name",
            "email",
            "phone",
            "companies",
            "applications",
        )
        self.contacts_table.update_data(
            self.engine,
            Contact,
            lambda c: (
                str(c.id),
                c.name,
                c.email,
                c.phone,
                str(len(c.companies)),
                str(len(c.applications)),
            ),
        )


if __name__ == "__main__":
    app = JoblessApp()
    app.run()
