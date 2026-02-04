from sqlalchemy.orm import sessionmaker
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.widgets import Footer

from jobless.constants import APP_NAME
from jobless.db import get_engine, init_db
from jobless.models import Application, Company, Contact
from jobless.repositories import (
    ApplicationRepository,
    CompanyRepository,
    ContactRepository,
    SkillRepository,
)
from jobless.settings import Settings
from jobless.widgets.datatables import (
    ApplicationTable,
    CompanyTable,
    ContactTable,
)
from jobless.widgets.header import AppHeader
from jobless.widgets.modals.confirmation_modal import ConfirmationModal
from jobless.widgets.modals.create_modals import (
    CreateApplicationModal,
    CreateCompanyModal,
    CreateContactModal,
)
from jobless.widgets.modals.edit_modals import EditCompanyModal


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

        init_db(self.engine)

    def compose(self) -> ComposeResult:
        yield AppHeader()

        with ScrollableContainer(classes="main"):
            yield CompanyTable(classes="table")
            yield ApplicationTable(classes="table")
            yield ContactTable(classes="table")

        yield Footer()

    def on_mount(self) -> None:
        self.theme = self.settings.theme

        self.SessionLocal = sessionmaker(bind=self.engine)

        self.companies_table = self.query_one(CompanyTable)
        self.applications_table = self.query_one(ApplicationTable)
        self.contacts_table = self.query_one(ContactTable)

        self.reload_tables()

    def action_reload(self) -> None:
        self.reload_tables()

    @on(CompanyTable.Create)
    def create_company(self) -> None:
        with self.SessionLocal() as session:
            contacts = ContactRepository(session).get_all()

        def callback(company: Company | None) -> None:
            if not company:
                return

            with self.SessionLocal() as session:
                CompanyRepository(session).add(company)
                session.commit()

            self.reload_tables()

        self.push_screen(
            CreateCompanyModal(contacts=contacts, title="new company"),
            callback=callback,
        )

    @on(ApplicationTable.Create)
    def create_application(self) -> None:
        with self.SessionLocal() as session:
            contacts = ContactRepository(session).get_all()
            companies = CompanyRepository(session).get_all()
            skills = SkillRepository(session).get_all()

        def callback(application: Application | None) -> None:
            if not application:
                return

            with self.SessionLocal() as session:
                ApplicationRepository(session).add(application)
                session.commit()

            self.reload_tables()

        self.push_screen(
            CreateApplicationModal(
                contacts=contacts,
                companies=companies,
                skills=skills,
                title="new application",
            ),
            callback=callback,
        )

    @on(ContactTable.Create)
    def create_contact(self) -> None:
        with self.SessionLocal() as session:
            applications = ApplicationRepository(session).get_all()
            companies = CompanyRepository(session).get_all()

        def callback(contact: Contact | None) -> None:
            if not contact:
                return

            with self.SessionLocal() as session:
                ContactRepository(session).add(contact)
                session.commit()

            self.reload_tables()

        self.push_screen(
            CreateContactModal(
                companies=companies, applications=applications, title="new contact"
            ),
            callback=callback,
        )

    @on(CompanyTable.Update)
    def update_company(self, message: CompanyTable.Update) -> None:
        with self.SessionLocal() as session:
            contacts = ContactRepository(session).get_all()
            company = CompanyRepository(session).get_by_id(message.id)

            assert company
            _ = company.contacts  # Load contact relationships

        if not company:
            return

        def callback(updated_company: Company | None) -> None:
            if not updated_company:
                return

            # with self.SessionLocal() as session:
            # TODO: update company
            # TODO: commit changes
            # pass

            self.reload_tables()

        self.push_screen(
            EditCompanyModal(
                title="update company details",
                instance=company,
                contacts=contacts,
            ),
            callback=callback,
        )

    @on(CompanyTable.Delete)
    def delete_company(self, message: CompanyTable.Delete) -> None:
        def callback(confirmed: bool | None) -> None:
            if not confirmed:
                return

            with self.SessionLocal() as session:
                CompanyRepository(session).delete(message.id)
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
                ApplicationRepository(session).delete(message.id)
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
                ContactRepository(session).delete(message.id)
                session.commit()

            self.reload_tables()

        self.push_screen(
            ConfirmationModal(message=f'delete "{message.name}" from contacts?'),
            callback=callback,
        )

    @work(thread=True, exclusive=True)
    def reload_tables(self) -> None:
        self.call_from_thread(setattr, self.applications_table, "loading", True)
        self.call_from_thread(setattr, self.companies_table, "loading", True)
        self.call_from_thread(setattr, self.contacts_table, "loading", True)

        with self.SessionLocal() as session:
            applications = ApplicationRepository(session).get_all()
            companies = CompanyRepository(session).get_all()
            contacts = ContactRepository(session).get_all()

            self.call_from_thread(
                self.applications_table.reload,
                [
                    self.applications_table.item_to_row(application)
                    for application in applications
                ],
            )
            self.call_from_thread(
                self.companies_table.reload,
                [self.companies_table.item_to_row(company) for company in companies],
            )
            self.call_from_thread(
                self.contacts_table.reload,
                [self.contacts_table.item_to_row(contact) for contact in contacts],
            )


if __name__ == "__main__":
    app = JoblessApp()
    app.run()
