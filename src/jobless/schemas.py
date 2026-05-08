from dataclasses import dataclass, field
from datetime import date

from email_validator import EmailNotValidError, validate_email

from jobless.enums import (
    ApplicationSortField,
    Location,
    SortOrder,
    Status,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class Skill:
    id: int | None = None
    name: str

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("skill name cannot be empty")


@dataclass(frozen=True, slots=True, kw_only=True)
class Company:
    id: int | None = None
    name: str
    url: str | None = None
    industry: str | None = None

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("company name cannot be empty")


@dataclass(frozen=True, slots=True, kw_only=True)
class Contact:
    id: int | None = None
    name: str
    email: str | None = None
    phone: str | None = None
    url: str | None = None

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("contact name cannot be empty")

        if self.email:
            try:
                validate_email(self.email, check_deliverability=False)
            except EmailNotValidError as e:
                raise ValueError(f"invalid email: {e}")


@dataclass(frozen=True, slots=True, kw_only=True)
class Application:
    id: int | None = None
    title: str
    description: str | None = None
    salary: str | None = None
    url: str | None = None
    location_type: Location = Location.ON_SITE
    status: Status = Status.SAVED
    date_applied: date | None = None
    follow_up_date: date | None = None
    notes: str | None = None
    company: Company
    contacts: list[Contact] = field(default_factory=list)
    skills: list[Skill] = field(default_factory=list)

    def __post_init__(self):
        if not self.title.strip():
            raise ValueError("application title cannot be empty")


@dataclass(slots=True, kw_only=True)
class ApplicationFilter:
    title: str | None = None
    statuses: list[Status] = field(default_factory=list)
    location_types: list[Location] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    company_name: str | None = None
    company_id: int | None = None
    applied_after: date | None = None
    applied_before: date | None = None
    follow_up_date_after: date | None = None
    follow_up_date_before: date | None = None

    sort_by: ApplicationSortField = ApplicationSortField.DATE_APPLIED
    sort_order: SortOrder = SortOrder.DESC

    limit: int | None = None
