from sqlalchemy.orm import sessionmaker
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.widgets import Footer

from jobless.constants import APP_NAME
from jobless.db import get_engine, init_db
from jobless.repositories import (
    ApplicationRepository,
    CompanyRepository,
    ContactRepository,
)
from jobless.settings import Settings
from jobless.widgets.datatables import (
    ApplicationTable,
    CompanyTable,
    ContactTable,
)
from jobless.widgets.header import AppHeader
from jobless.widgets.modals.confirmation_modal import ConfirmationModal


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
            self.companies_table = CompanyTable(
                id="companies",
                classes="table companies",
            )
            yield self.companies_table

            self.applications_table = ApplicationTable(
                id="applications",
                classes="table applications",
            )
            yield self.applications_table

            self.contacts_table = ContactTable(
                id="contacts",
                classes="table contacts",
            )
            yield self.contacts_table

        yield Footer()

    def on_mount(self) -> None:
        init_db(self.engine)

        self.SessionLocal = sessionmaker(bind=self.engine)

        self.theme = self.settings.theme
        self.reload_tables()

    def action_reload(self) -> None:
        self.reload_tables()

    @on(CompanyTable.Delete)
    def delete_company(self, message: CompanyTable.Delete) -> None:
        def callback(confirmed: bool | None) -> None:
            if not confirmed:
                return

            with self.SessionLocal() as session:
                company_repo = CompanyRepository(session)
                company_repo.delete(message.id)
                session.commit()

            self.reload_tables()

        self.push_screen(
            ConfirmationModal(message=f'delete "{message.name}" from companies?'),
            callback=callback,
        )

    @on(ApplicationTable.Delete)
    def delete_application(self, message: ApplicationTable.Delete) -> None:
        def callback(confirmed: bool | None) -> None:
            if not confirmed:
                return

            with self.SessionLocal() as session:
                application_repo = ApplicationRepository(session)
                application_repo.delete(message.id)
                session.commit()

            self.reload_tables()

        self.push_screen(
            ConfirmationModal(message=f'delete "{message.name}" from applications?'),
            callback=callback,
        )

    @on(ContactTable.Delete)
    def delete_contact(self, message: ContactTable.Delete) -> None:
        def callback(confirmed: bool | None) -> None:
            if not confirmed:
                return

            with self.SessionLocal() as session:
                contact_repo = ContactRepository(session)
                contact_repo.delete(message.id)
                session.commit()

            self.reload_tables()

        self.push_screen(
            ConfirmationModal(message=f'delete "{message.name}" from contacts?'),
            callback=callback,
        )

    def add_contact(self) -> None:
        # def callback(contact: Contact | None) -> None:
        #     if not contact:
        #         return
        #
        #     with get_session(self.engine) as session:
        #         add_contact(session, contact)
        #         self.notify(f'new contact "{contact.name}" added')
        #     self.reload_tables()
        #
        # self.push_screen(NewContactModal(), callback=callback)
        pass

    @work(thread=True, exclusive=True)
    def reload_tables(self) -> None:
        self.call_from_thread(setattr, self.applications_table, "loading", True)
        self.call_from_thread(setattr, self.companies_table, "loading", True)
        self.call_from_thread(setattr, self.contacts_table, "loading", True)

        with self.SessionLocal() as session:
            application_repo = ApplicationRepository(session)
            company_repo = CompanyRepository(session)
            contact_repo = ContactRepository(session)

            self.call_from_thread(
                self.applications_table.reload,
                [
                    self.applications_table.item_to_row(application)
                    for application in application_repo.get_all()
                ],
            )
            self.call_from_thread(
                self.companies_table.reload,
                [
                    self.companies_table.item_to_row(company)
                    for company in company_repo.get_all()
                ],
            )
            self.call_from_thread(
                self.contacts_table.reload,
                [
                    self.contacts_table.item_to_row(contact)
                    for contact in contact_repo.get_all()
                ],
            )


if __name__ == "__main__":
    app = JoblessApp()
    app.run()
