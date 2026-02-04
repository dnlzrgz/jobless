from datetime import date, datetime

from pydantic import ValidationError
from textual.app import ComposeResult
from textual.suggester import SuggestFromList
from textual.widgets import Input, Label, Select, SelectionList, TextArea

from jobless.models import Application, Company, Contact, Location, Skill, Status
from jobless.schemas import ApplicationCreate, CompanyCreate, ContactCreate
from jobless.widgets.modals.base_form_modals import FormModal


class CreateCompanyModal(FormModal[Company]):
    def __init__(
        self,
        contacts: list[Contact] = [],
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.contacts = contacts

    def compose_form(self) -> ComposeResult:
        yield Label("name")
        yield Input(
            placeholder="Company SA",
            id="name",
        )

        yield Label("website")
        yield Input(
            placeholder="https://company.com",
            valid_empty=True,
            id="website",
        )

        yield Label("industry")
        yield Input(
            placeholder="IT",
            valid_empty=True,
            id="industry",
        )

        yield Label("contacts")
        yield SelectionList[int](
            *[(contact.name, contact.id) for contact in self.contacts],
            id="contacts",
        )

        yield Label("notes")
        yield TextArea(
            placeholder="Anything that comes to mind.",
            id="notes",
        )

    def get_result(self) -> Company | None:
        form_data = {
            "name": self.query_one("#name", Input).value,
            "website": self.query_one("#website", Input).value or None,
            "industry": self.query_one("#industry", Input).value or None,
            "contact_ids": self.query_one("#contacts", SelectionList).selected,
            "notes": self.query_one("#notes", TextArea).text or None,
        }

        try:
            validated_data = CompanyCreate(**form_data)
            data_dict = validated_data.model_dump(exclude={"contact_ids"})
            company = Company(**data_dict)
            company.contacts = [
                contact
                for contact in self.contacts
                if contact.id in validated_data.contact_ids
            ]
            return company
        except ValidationError as e:
            self.notify_validation_errors(e)


class CreateContactModal(FormModal[Contact]):
    def __init__(
        self,
        companies: list[Company] = [],
        applications: list[Application] = [],
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.companies = companies
        self.applications = applications

    def compose_form(self) -> ComposeResult:
        yield Label("name")
        yield Input(
            placeholder="john doe",
            id="name",
        )

        yield Label("email")
        yield Input(
            placeholder="john@doe.com",
            valid_empty=True,
            id="email",
        )

        yield Label("phone number")
        yield Input(
            placeholder="(555) 010-0001",
            valid_empty=True,
            id="phone",
        )

        yield Label("url")
        yield Input(
            placeholder="johndoe.com",
            valid_empty=True,
            id="url",
        )

        yield Label("companies")
        yield SelectionList[int](
            *[(company.name, company.id) for company in self.companies],
            id="companies",
        )

        yield Label("applications")
        yield SelectionList[int](
            *[(application.title, application.id) for application in self.applications],
            id="applications",
        )

        yield Label("notes")
        yield TextArea(
            placeholder="Anything that comes to mind.",
            id="notes",
        )

    def get_result(self) -> Contact | None:
        form_data = {
            "name": self.query_one("#name", Input).value,
            "email": self.query_one("#email", Input).value or None,
            "phone": self.query_one("#phone", Input).value or None,
            "url": self.query_one("#url", Input).value or None,
            "notes": self.query_one("#notes", TextArea).text or None,
            "company_ids": self.query_one("#companies", SelectionList).selected,
            "application_ids": self.query_one("#applications", SelectionList).selected,
        }

        try:
            validated_data = ContactCreate(**form_data)
            scalar_data = validated_data.model_dump(
                exclude={"company_ids", "application_ids"},
                exclude_unset=True,
            )
            contact = Contact(**scalar_data)

            contact.companies = [
                company
                for company in self.companies
                if company.id in validated_data.company_ids
            ]
            contact.applications = [
                application
                for application in self.applications
                if application.id in validated_data.application_ids
            ]

            return contact
        except ValidationError as e:
            self.notify_validation_errors(e)


class CreateApplicationModal(FormModal[Application]):
    def __init__(
        self,
        companies: list[Company] = [],
        contacts: list[Contact] = [],
        skills: list[Skill] = [],
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.companies = companies
        self.contacts = contacts
        self.skills = skills

    def compose_form(self) -> ComposeResult:
        yield Label("title")
        yield Input(
            placeholder="Title",
            id="title",
        )

        yield Label("company")
        yield Select(
            options=[(company.name, company.id) for company in self.companies],
            prompt="select a company",
            id="company",
        )

        yield Label("description")
        yield TextArea(
            placeholder="Job description",
            id="description",
        )

        yield Label("skills")
        yield Input(
            suggester=SuggestFromList(
                [skill.name for skill in self.skills],
                case_sensitive=False,
            ),
            placeholder="e.g. python, rust, sql, git...",
            valid_empty=True,
            id="skills",
        )

        yield Label("salary range")
        yield Input(
            placeholder="e.g. $125k - $150k",
            valid_empty=True,
            id="salary",
        )

        yield Label("platform")
        yield Input(
            placeholder="LinkedIn",
            valid_empty=True,
            id="platform",
        )

        yield Label("url")
        yield Input(
            placeholder="https://...",
            valid_empty=True,
            id="url",
        )

        yield Label("location type")
        yield Select(
            options=[
                (location_type.value, location_type) for location_type in Location
            ],
            value=Location.ON_SITE,
            id="location",
        )

        yield Label("status")
        yield Select(
            options=[(status.value, status) for status in Status],
            value=Status.SAVED,
            id="status",
        )

        yield Label("priority (0-4)")
        yield Input(
            placeholder="0",
            type="integer",
            id="priority",
        )

        yield Label("date applied")
        yield Input(placeholder="YYYY-MM-DD", id="date_applied")

        yield Label("follow up date")
        yield Input(placeholder="YYYY-MM-DD", id="follow_up_date")

        yield Label("address")
        yield Input(
            placeholder="123 Tech Lane, San Francisco, CA",
            valid_empty=True,
            id="address",
        )

        yield Label("contacts")
        yield SelectionList[int](
            *[(contact.name, contact.id) for contact in self.contacts],
            id="contacts",
        )

        yield Label("notes")
        yield TextArea(
            placeholder="Anything that comes to mind.",
            id="notes",
        )

    def parse_date(self, field_name: str, value: str) -> date | None:
        if not value:
            return None

        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            self.notify(
                f"'{value}' is not a valid date",
                title=f"invalid {field_name}",
                severity="error",
            )
            return None

    def get_result(self) -> Application | None:
        company_id = self.query_one("#company", Select).value
        if company_id == Select.BLANK:
            self.notify("A company is required", severity="error")
            return None

        raw_skills = self.query_one("#skills", Input).value
        skill_names = [
            name.strip().lower() for name in raw_skills.split(",") if name.strip()
        ]

        date_applied = self.parse_date(
            "applied date", self.query_one("#date_applied", Input).value
        )
        follow_up_date = self.parse_date(
            "follow up date", self.query_one("#follow_up_date", Input).value
        )

        form_data = {
            "title": self.query_one("#title", Input).value,
            "description": self.query_one("#description", TextArea).text or None,
            "company_id": company_id,
            "salary_range": self.query_one("#salary", Input).value or None,
            "platform": self.query_one("#platform", Input).value or None,
            "url": self.query_one("#url", Input).value or None,
            "address": self.query_one("#address", Input).value or None,
            "location_type": self.query_one("#location", Select).value,
            "status": self.query_one("#status", Select).value,
            "priority": int(self.query_one("#priority", Input).value or 0),
            "date_applied": date_applied,
            "follow_up_date": follow_up_date,
            "notes": self.query_one("#notes", TextArea).text or None,
            "skill_names": skill_names,
            "contact_ids": self.query_one("#contacts", SelectionList).selected,
        }

        try:
            validated_data = ApplicationCreate(**form_data)
            scalar_data = validated_data.model_dump(
                exclude={"skill_names", "contact_ids"},
                exclude_unset=True,
            )
            application = Application(**scalar_data)

            application.contacts = [
                contact
                for contact in self.contacts
                if contact.id in validated_data.contact_ids
            ]

            existing_skills = {s.name.lower(): s for s in self.skills}
            application.skills = [
                existing_skills.get(name, Skill(name=name))
                for name in validated_data.skill_names
            ]

            return application
        except ValidationError as e:
            self.notify_validation_errors(e)
