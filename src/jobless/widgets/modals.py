from datetime import datetime
from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.css.query import NoMatches
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Input,
    Label,
    Select,
    SelectionList,
    Static,
    TextArea,
)

from jobless.models import Location, Status
from jobless.schemas import (
    ApplicationSchema,
    CompanySchema,
    ContactSchema,
    LookupSchema,
)


def _to_options(items: list[LookupSchema]) -> list[tuple[str, int]]:
    return [(item.label, item.id) for item in items if item.id]


class FormModal(ModalScreen[dict]):
    """
    Base class for all Jobless modals that act as a form.
    """

    BINDINGS = [
        Binding(
            "escape",
            "dismiss(None)",
            description="cancel",
        ),
    ]

    def __init__(
        self,
        title: str,
        cancel_label: str = "cancel",
        submit_label: str = "save",
        *args,
        **kwargs,
    ) -> None:
        self.form_title = title
        self.cancel_label = cancel_label
        self.submit_label = submit_label
        super().__init__(*args, **kwargs)

    def compose_form(self) -> ComposeResult:
        """
        Override to add specific inputs.
        """
        yield from []

    def get_result(self) -> dict[str, Any] | None:
        """
        Override this to return data from the inputs.
        """
        raise NotImplementedError

    def compose(self) -> ComposeResult:
        with VerticalScroll(classes="form") as vs:
            vs.border_title = self.form_title
            yield from self.compose_form()

            yield Horizontal(
                Button(
                    self.cancel_label,
                    variant="error",
                    id="cancel",
                ),
                Button(
                    self.submit_label,
                    variant="success",
                    id="submit",
                ),
                classes="buttons",
            )

    def on_mount(self) -> None:
        try:
            first_input = self.query(Input).first()
            first_input.focus()
        except NoMatches:
            return

    @on(Button.Pressed, "#cancel")
    def on_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#submit")
    def on_submit(self) -> None:
        result = self.get_result()
        if result:
            self.dismiss(result)


class ConfirmationModal(FormModal):
    BINDINGS = FormModal.BINDINGS + [
        Binding(
            "y,enter",
            "submit",
            description="confirm",
            priority=True,
        ),
    ]

    def __init__(self, message: str, *args, **kwargs) -> None:
        self.message = message
        super().__init__(title="confirm", submit_label="confirm", *args, **kwargs)

    def compose_form(self) -> ComposeResult:
        yield Static(self.message, id="message")

    def get_result(self) -> dict[str, Any] | None:
        return {"confirmed": True}

    def action_submit(self) -> None:
        self.on_submit()


class CreateCompanyModal(FormModal):
    def __init__(
        self,
        contacts: list[LookupSchema],
        known_names: set[str],
        known_urls: set[str],
        title: str = "add a new company",
        *args,
        **kwargs,
    ) -> None:
        self.contacts = contacts
        self.known_names = known_names
        self.known_urls = known_urls
        super().__init__(title=title, *args, **kwargs)

    def compose_form(self) -> ComposeResult:
        yield Label("name")
        yield Input(
            placeholder="e.g. acme",
            id="name",
        )

        yield Label("url")
        yield Input(
            placeholder="https://acme.com",
            id="url",
        )

        yield Label("industry")
        yield Input(
            placeholder="e.g. fintech, healthcare, education",
            id="industry",
        )

        yield Label("contacts")
        yield SelectionList[int](
            *_to_options(self.contacts),
            id="contacts",
        )

        yield Label("notes")
        yield TextArea(
            placeholder="details about the company...",
            id="notes",
        )

    def get_result(self) -> dict[str, Any] | None:
        name = self.query_one("#name", Input).value.strip()
        url = self.query_one("#url", Input).value.strip() or None

        if not name:
            self.notify("name can not be empty!", severity="error")
            self.query_one("#name", Input).focus()
            return None

        if name in self.known_names:
            self.notify(f"a company '{name}' already exists!", severity="error")
            self.query_one("#name", Input).focus()
            return None

        if url and url in self.known_urls:
            self.notify(f"the url '{url}' already exists!", severity="error")
            self.query_one("#url", Input).focus()
            return None

        selected_contacts = self.query_one("#contacts", SelectionList).selected
        contacts = [
            contact for contact in self.contacts if contact.id in selected_contacts
        ]

        return {
            "name": name,
            "url": url,
            "industry": self.query_one("#industry", Input).value.strip() or None,
            "contacts": contacts,
            "notes": self.query_one("#notes", TextArea).text.strip() or None,
        }


class CreateContactModal(FormModal):
    def __init__(
        self,
        companies: list[LookupSchema],
        applications: list[LookupSchema],
        known_emails: set[str],
        known_urls: set[str],
        known_phones: set[str],
        title: str = "add a new contact",
        *args,
        **kwargs,
    ) -> None:
        self.applications = applications
        self.companies = companies
        self.known_emails = known_emails
        self.known_urls = known_urls
        self.known_phones = known_phones
        super().__init__(title=title, *args, **kwargs)

    def compose_form(self) -> ComposeResult:
        yield Label("name")
        yield Input(placeholder="e.g. john doe", id="name")

        yield Label("email")
        yield Input(placeholder="john@doe.com", id="email")

        yield Label("phone number")
        yield Input(placeholder="+1 (555) 000-0000", id="phone")

        yield Label("url")
        yield Input(placeholder="linkedin.com/in/jonhdoe", id="url")

        yield Label("companies")
        yield SelectionList[int](
            *_to_options(self.companies),
            id="companies",
        )

        yield Label("applications")
        yield SelectionList[int](
            *_to_options(self.applications),
            id="applications",
        )

        yield Label("notes")
        yield TextArea(
            placeholder="where did you meet? what makes this person interesting?",
            id="notes",
        )

    def get_result(self) -> dict[str, Any] | None:
        name = self.query_one("#name", Input).value.strip()
        email = self.query_one("#email", Input).value.strip() or None
        url = self.query_one("#url", Input).value.strip() or None
        phone = self.query_one("#phone", Input).value.strip() or None

        if not name:
            self.notify("name can not be empty!", severity="error")
            self.query_one("#name", Input).focus()
            return None

        if email and email in self.known_emails:
            self.notify(f"email '{email}' already exists!", severity="error")
            return None

        if url and url in self.known_urls:
            self.notify(f"url '{url}' already exists!", severity="error")
            return None

        if phone and phone in self.known_phones:
            self.notify(f"phone '{phone}' already exists!", severity="error")
            return None

        selected_companies = self.query_one("#companies", SelectionList).selected
        companies = [
            company for company in self.companies if company.id in selected_companies
        ]

        selected_applications = self.query_one("#applications", SelectionList).selected
        applications = [
            application
            for application in self.applications
            if application.id in selected_applications
        ]

        return {
            "name": name,
            "email": email,
            "url": url,
            "phone": phone,
            "companies": companies,
            "applications": applications,
            "notes": self.query_one("#notes", TextArea).text.strip() or None,
        }


class CreateApplicationModal(FormModal):
    def __init__(
        self,
        companies: list[LookupSchema],
        contacts: list[LookupSchema],
        skills: list[LookupSchema],
        known_urls: set[str],
        title: str = "add a new application",
        *args,
        **kwargs,
    ) -> None:
        self.companies = companies
        self.contacts = contacts
        self.skills = skills
        self.known_urls = known_urls
        super().__init__(title=title, *args, **kwargs)

    def compose_form(self) -> ComposeResult:
        yield Label("job title")
        yield Input(placeholder="e.g. senior python developer", id="title")

        yield Label("job description")
        yield TextArea(
            placeholder="requirements or the job post content here...",
            id="description",
        )

        yield Label("company")
        yield Select[int](
            options=_to_options(self.companies),
            id="company_id",
        )

        yield Label("status")
        yield Select(
            options=[(status.value, status) for status in Status],
            value=Status.SAVED,
            allow_blank=False,
            id="status",
        )

        yield Label("priority")
        yield Input(
            placeholder="0 (low) to 4 (high)",
            type="integer",
            id="priority",
        )

        yield Label("platform")
        yield Input(placeholder="e.g. linkedin, indeed,...", id="platform")

        yield Label("salary range")
        yield Input(placeholder="e.g. 80k - 110k", id="salary")

        yield Label("location")
        yield Select(
            options=[(location.value, location) for location in Location],
            value=Location.ON_SITE,
            allow_blank=False,
            id="location",
        )

        yield Label("address")
        yield Input(placeholder="e.g. 123 Tech Lane", id="address")

        yield Label("date applied")
        yield Input(placeholder="YYYY-MM-DD", id="date_applied")

        yield Label("follow up date")
        yield Input(placeholder="YYYY-MM-DD", id="follow_up_date")

        yield Label("contacts")
        yield SelectionList[int](
            *_to_options(self.contacts),
            id="contacts",
        )

        yield Label("skills")
        yield Input(
            placeholder="e.g. python, textual, sql, postgresql",
            id="skills",
        )

        yield Label("notes")
        yield TextArea(
            placeholder="thoughts after applying, interviewing highlights...",
            id="notes",
        )

    def _parse_date(self, value: str):
        if not value:
            return None

        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return "INVALID"

    def get_result(self) -> dict[str, Any] | None:
        title = self.query_one("#title", Input).value.strip()
        company_id = self.query_one("#company_id", Select).value

        if not title or company_id == Select.NULL:
            self.notify("a title and a company are required!", severity="error")
            return None

        assert isinstance(company_id, int)

        date_applied = self._parse_date(
            self.query_one("#date_applied", Input).value.strip()
        )
        if date_applied == "INVALID":
            self.notify("applied date is not a valid date!", severity="error")
            return None

        follow_up_date = self._parse_date(
            self.query_one("#follow_up_date", Input).value.strip()
        )
        if follow_up_date == "INVALID":
            self.notify("follow up date is not a valid date!", severity="error")
            return None

        selected_contacts = self.query_one("#contacts", SelectionList).selected
        contacts = [
            contact for contact in self.contacts if contact.id in selected_contacts
        ]

        raw_skills = self.query_one("#skills", Input).value.strip()
        skills = [
            LookupSchema(label=skill.strip())
            for skill in raw_skills.split(",")
            if skill.strip()
        ]

        return {
            "title": title,
            "description": self.query_one("#description", TextArea).text.strip()
            or None,
            "company": LookupSchema(id=company_id, label=""),
            "status": self.query_one("#status", Select).value,
            "priority": int(self.query_one("#priority", Input).value or 0),
            "platform": self.query_one("#platform", Input).value.strip() or None,
            "salary_range": self.query_one("#salary", Input).value.strip() or None,
            "location_type": self.query_one("#location", Select).value,
            "address": self.query_one("#address", Input).value.strip() or None,
            "date_applied": date_applied,
            "follow_up_date": follow_up_date,
            "contacts": contacts,
            "skills": skills,
            "notes": self.query_one("#notes", TextArea).text.strip() or None,
        }


class UpdateCompanyModal(CreateCompanyModal):
    def __init__(
        self,
        instance: CompanySchema,
        contacts: list[LookupSchema],
        known_names: set[str],
        known_urls: set[str],
        title: str = "update company",
        *args,
        **kwargs,
    ) -> None:
        self.instance = instance

        safe_names = known_names - {self.instance.name}
        safe_urls = known_urls - {self.instance.url}

        super().__init__(
            contacts=contacts,
            known_names=safe_names,
            known_urls=safe_urls,
            title=title,
            *args,
            **kwargs,
        )

    def on_mount(self) -> None:
        super().on_mount()

        self.query_one("#name", Input).value = self.instance.name
        self.query_one("#url", Input).value = self.instance.url or ""
        self.query_one("#industry", Input).value = self.instance.industry or ""
        self.query_one("#notes", TextArea).text = self.instance.notes or ""

        selection_list = self.query_one("#contacts", SelectionList)
        selected_contacts = [contact.id for contact in self.instance.contacts]
        for contact_id in selected_contacts:
            selection_list.select(contact_id)


class UpdateContactModal(CreateContactModal):
    def __init__(
        self,
        instance: ContactSchema,
        companies: list[LookupSchema],
        applications: list[LookupSchema],
        known_emails: set[str],
        known_urls: set[str],
        known_phones: set[str],
        title: str = "update contact",
        *args,
        **kwargs,
    ) -> None:
        self.instance = instance

        safe_emails = known_emails - {self.instance.email}
        safe_urls = known_urls - {self.instance.url}
        safe_phones = known_phones - {self.instance.phone}

        super().__init__(
            companies=companies,
            applications=applications,
            known_emails=safe_emails,
            known_urls=safe_urls,
            known_phones=safe_phones,
            title=title,
            *args,
            **kwargs,
        )

    def on_mount(self) -> None:
        super().on_mount()

        self.query_one("#name", Input).value = self.instance.name
        self.query_one("#email", Input).value = self.instance.email or ""
        self.query_one("#phone", Input).value = self.instance.phone or ""
        self.query_one("#url", Input).value = self.instance.url or ""
        self.query_one("#notes", TextArea).text = self.instance.notes or ""

        company_selection_list = self.query_one("#companies", SelectionList)
        selected_companies = [company.id for company in self.instance.companies]
        for company_id in selected_companies:
            company_selection_list.select(company_id)

        application_selection_list = self.query_one("#applications", SelectionList)
        selected_applications = [
            application.id for application in self.instance.applications
        ]
        for application_id in selected_applications:
            application_selection_list.select(application_id)


class UpdateApplicationModal(CreateApplicationModal):
    def __init__(
        self,
        instance: ApplicationSchema,
        companies: list[LookupSchema],
        contacts: list[LookupSchema],
        skills: list[LookupSchema],
        known_urls: set[str],
        title: str = "update application",
        *args,
        **kwargs,
    ) -> None:
        self.instance = instance

        safe_urls = known_urls - {self.instance.url}

        super().__init__(
            companies=companies,
            contacts=contacts,
            skills=skills,
            known_urls=safe_urls,
            title=title,
            *args,
            **kwargs,
        )

    def on_mount(self) -> None:
        super().on_mount()

        self.query_one("#title", Input).value = self.instance.title
        self.query_one("#priority", Input).value = str(self.instance.priority)
        self.query_one("#platform", Input).value = self.instance.platform or ""
        self.query_one("#salary", Input).value = self.instance.salary_range or ""
        self.query_one("#address", Input).value = self.instance.address or ""
        self.query_one("#skills", Input).value = ", ".join(
            [skill.label for skill in self.instance.skills if skill.label]
        )

        if self.instance.date_applied:
            self.query_one(
                "#date_applied",
                Input,
            ).value = self.instance.date_applied.strftime("%Y-%m-%d")

        if self.instance.follow_up_date:
            self.query_one(
                "#follow_up_date",
                Input,
            ).value = self.instance.follow_up_date.strftime("%Y-%m-%d")

        self.query_one("#description", TextArea).text = self.instance.description or ""
        self.query_one("#notes", TextArea).text = self.instance.notes or ""

        self.query_one("#company_id", Select).value = self.instance.company.id
        self.query_one("#status", Select).value = self.instance.status
        self.query_one("#location", Select).value = self.instance.location_type

        selection_list = self.query_one("#contacts", SelectionList)
        selected_contacts = [contact.id for contact in self.instance.contacts]
        for contact_id in selected_contacts:
            selection_list.select(contact_id)
