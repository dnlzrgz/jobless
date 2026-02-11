from typing import Callable, Type, TypedDict

from sqlalchemy.orm import sessionmaker
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import Footer

from jobless.constants import APP_NAME
from jobless.db import get_engine, init_db
from jobless.repositories import (
    ApplicationRepository,
    CompanyRepository,
    ContactRepository,
    GenericRepository,
    SkillRepository,
)
from jobless.settings import Settings
from jobless.widgets.datatables import (
    ApplicationTable,
    CompanyTable,
    ContactTable,
    JoblessTable,
)
from jobless.widgets.header import AppHeader
from jobless.widgets.modals import (
    ConfirmationModal,
    CreateApplicationModal,
    CreateCompanyModal,
    CreateContactModal,
)


class TableConfig(TypedDict):
    instance: JoblessTable
    repository: GenericRepository
    label: str
    create_modal_launcher: Callable[[], Screen]


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

        engine = get_engine(self.settings.db_url)
        init_db(engine)
        session_factory = sessionmaker(bind=engine, expire_on_commit=False)

        self.company_repository = CompanyRepository(session_factory)
        self.application_repository = ApplicationRepository(session_factory)
        self.skill_repository = SkillRepository(session_factory)
        self.contact_repository = ContactRepository(session_factory)

    def compose(self) -> ComposeResult:
        yield AppHeader()

        with ScrollableContainer(classes="main"):
            self.company_table = CompanyTable(classes="table")
            yield self.company_table

            self.application_table = ApplicationTable(classes="table")
            yield self.application_table

            self.contact_table = ContactTable(classes="table")
            yield self.contact_table

        yield Footer()

    def on_mount(self) -> None:
        self.theme = self.settings.theme

        self.registry: dict[Type[JoblessTable], TableConfig] = {
            CompanyTable: {
                "instance": self.company_table,
                "repository": self.company_repository,
                "label": "company",
                "create_modal_launcher": self._make_create_company_modal,
            },
            ApplicationTable: {
                "instance": self.application_table,
                "repository": self.application_repository,
                "label": "application",
                "create_modal_launcher": self._make_create_application_modal,
            },
            ContactTable: {
                "instance": self.contact_table,
                "repository": self.contact_repository,
                "label": "contact",
                "create_modal_launcher": self._make_create_contact_modal,
            },
        }

        self.action_reload()

    def action_reload(self) -> None:
        for config in self.registry.values():
            self.reload_table(config)

    def _make_create_company_modal(self) -> CreateCompanyModal:
        contacts = self.contact_repository.list()
        known_names = self.company_repository.list_names()
        known_urls = self.company_repository.list_urls()

        return CreateCompanyModal(
            contacts=contacts,
            known_names=known_names,
            known_urls=known_urls,
        )

    def _make_create_contact_modal(self) -> CreateContactModal:
        companies = self.company_repository.list()
        applications = self.application_repository.list()
        known_phones = self.contact_repository.list_phones()
        known_emails = self.contact_repository.list_emails()
        known_urls = self.contact_repository.list_urls()

        return CreateContactModal(
            companies=companies,
            applications=applications,
            known_phones=known_phones,
            known_emails=known_emails,
            known_urls=known_urls,
        )

    def _make_create_application_modal(self) -> CreateApplicationModal:
        companies = self.company_repository.list()
        contacts = self.contact_repository.list()
        known_urls = self.application_repository.list_urls()

        return CreateApplicationModal(
            companies=companies,
            contacts=contacts,
            known_urls=known_urls,
        )

    @on(JoblessTable.Delete)
    def handle_delete(self, message: JoblessTable.Delete) -> None:
        config: TableConfig | None = self.registry.get(type(message.table))
        if not config:
            return

        repository = config["repository"]
        label = config["label"]

        item = repository.get_by_id(message.id)
        if not item:
            self.notify(f"{label} not found!", severity="error")
            return

        def callback(result: dict | None) -> None:
            if result:
                repository.delete(item.id)
                self.notify(f"{label} deleted!")
                self.action_reload()

        display_name = getattr(item, "name", getattr(item, "title", "name"))
        self.push_screen(
            ConfirmationModal(
                message=f'delete {label} "{display_name}"?',
            ),
            callback,
        )

    @on(JoblessTable.Create)
    def handle_create(self, message: JoblessTable.Create) -> None:
        config: TableConfig | None = self.registry.get(type(message.table))
        if not config:
            return

        label = config["label"]
        repository = config["repository"]
        create_modal = config["create_modal_launcher"]()

        def callback(result: dict | None) -> None:
            if not result:
                return

            try:
                model_instance = repository.model(**result)
                repository.add(model_instance)
                self.notify(f"new {label} added!")
                self.action_reload()
            except Exception as e:
                self.notify(f"could not add new {label}: {e}", severity="error")

        self.push_screen(create_modal, callback)

    @work(thread=True)
    def reload_table(self, config: dict) -> None:
        table = config["instance"]
        repository = config["repository"]

        self.call_from_thread(setattr, table, "loading", True)

        try:
            items = repository.list_with_details()
            rows = [table.item_to_row(item) for item in items]
            self.call_from_thread(table.reload, rows)
        finally:
            self.call_from_thread(setattr, table, "loading", False)


if __name__ == "__main__":
    app = JoblessApp()
    app.run()
