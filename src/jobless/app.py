from contextlib import contextmanager
from sqlalchemy.orm import scoped_session, sessionmaker
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
from jobless.schemas import ApplicationCreate, CompanyCreate, ContactCreate
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

    @contextmanager
    def local_session(self):
        session = self.session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.notify(f"something went wrong: {e}", severity="error")
        finally:
            self.session.remove()

    def __init__(self):
        super().__init__()

        self.settings: Settings = Settings()
        self.engine = get_engine(self.settings.db_url)

        init_db(self.engine)
        session_factory = sessionmaker(bind=self.engine)
        self.session = scoped_session(session_factory)

    def compose(self) -> ComposeResult:
        yield AppHeader()

        with ScrollableContainer(classes="main"):
            yield CompanyTable(classes="table")
            yield ApplicationTable(classes="table")
            yield ContactTable(classes="table")

        yield Footer()

    def on_mount(self) -> None:
        self.theme = self.settings.theme

        self.companies_table = self.query_one(CompanyTable)
        self.applications_table = self.query_one(ApplicationTable)
        self.contacts_table = self.query_one(ContactTable)

        self.reload_tables()

    def action_reload(self) -> None:
        self.reload_tables()

    @on(CompanyTable.Create)
    def create_company(self) -> None:
        with self.local_session() as session:
            contacts = ContactRepository(session).get_all()
            session.expunge_all()

        def callback(schema: CompanyCreate | None) -> None:
            if not schema:
                return

            with self.local_session() as session:
                new_company = Company(**schema.model_dump(exclude={"contact_ids"}))
                if schema.contact_ids:
                    new_company.contacts = ContactRepository(session).get_by_ids(
                        schema.contact_ids
                    )

                    CompanyRepository(session).add(new_company)
                    self.notify(f"company '{new_company.name}' added!")

            self.reload_tables()

        self.push_screen(
            CreateCompanyModal(contacts=contacts, title="new company"),
            callback=callback,
        )

    @on(ApplicationTable.Create)
    def create_application(self) -> None:
        with self.local_session() as session:
            contacts = ContactRepository(session).get_all()
            companies = CompanyRepository(session).get_all()
            skills = SkillRepository(session).get_all()
            session.expunge_all()

        def callback(schema: ApplicationCreate | None) -> None:
            if not schema:
                return

            with self.local_session() as session:
                new_application = Application(
                    **schema.model_dump(exclude={"contact_ids", "skill_names"})
                )

                if schema.contact_ids:
                    new_application.contacts = ContactRepository(session).get_by_ids(
                        schema.contact_ids
                    )

                if schema.skill_names:
                    new_application.skills = SkillRepository(session).get_by_ids(
                        schema.skill_names
                    )

                ApplicationRepository(session).add(new_application)
                self.notify("new application added!")

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
        with self.local_session() as session:
            applications = ApplicationRepository(session).get_all()
            companies = CompanyRepository(session).get_all()
            session.expunge_all()

        def callback(schema: ContactCreate | None) -> None:
            if not schema:
                return

            with self.local_session() as session:
                new_contact = Contact(
                    **schema.model_dump(exclude={"company_ids", "application_ids"})
                )

                if schema.application_ids:
                    new_contact.applications = ApplicationRepository(
                        session
                    ).get_by_ids(schema.application_ids)

                if schema.company_ids:
                    new_contact.companies = CompanyRepository(session).get_by_ids(
                        schema.company_ids
                    )

                ContactRepository(session).add(new_contact)
                self.notify(f"new contact '{new_contact.name}' added!")

            self.reload_tables()

        self.push_screen(
            CreateContactModal(
                companies=companies, applications=applications, title="new contact"
            ),
            callback=callback,
        )

    @on(CompanyTable.Delete)
    def delete_company(self, message: CompanyTable.Delete) -> None:
        def callback(confirmed: bool | None) -> None:
            if confirmed:
                with self.local_session() as session:
                    CompanyRepository(session).delete(message.id)
                    self.notify("company removed successfully!")

                self.reload_tables()

        self.push_screen(
            ConfirmationModal(message=f'delete "{message.name}" from companies?'),
            callback=callback,
        )

    @on(ApplicationTable.Delete)
    def delete_application(self, message: ApplicationTable.Delete) -> None:
        def callback(confirmed: bool | None) -> None:
            if confirmed:
                with self.local_session() as session:
                    ApplicationRepository(session).delete(message.id)
                    self.notify("application removed successfully!")

                self.reload_tables()

        self.push_screen(
            ConfirmationModal(message=f'delete "{message.name}" from applications?'),
            callback=callback,
        )

    @on(ContactTable.Delete)
    def delete_contact(self, message: ContactTable.Delete) -> None:
        def callback(confirmed: bool | None) -> None:
            if confirmed:
                with self.local_session() as session:
                    ContactRepository(session).delete(message.id)
                    self.notify("contact removed sucsessfully!")

                self.reload_tables()

        self.push_screen(
            ConfirmationModal(message=f'delete "{message.name}" from contacts?'),
            callback=callback,
        )

    @work(thread=True, exclusive=True)
    def reload_tables(self) -> None:
        tables = [self.applications_table, self.companies_table, self.contacts_table]

        for table in tables:
            self.call_from_thread(setattr, table, "loading", True)

        try:
            with self.local_session() as session:
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
                    [
                        self.companies_table.item_to_row(company)
                        for company in companies
                    ],
                )
                self.call_from_thread(
                    self.contacts_table.reload,
                    [self.contacts_table.item_to_row(contact) for contact in contacts],
                )
        finally:
            for table in tables:
                self.call_from_thread(setattr, table, "loading", False)


if __name__ == "__main__":
    app = JoblessApp()
    app.run()
