from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum


class Status(StrEnum):
    SAVED = "Saved"
    APPLIED = "Applied"
    INTERVIEWING = "Interviewing"
    OFFER = "Offer"
    REJECTED = "Rejected"
    GHOSTED = "Ghosted"


class Location(StrEnum):
    REMOTE = "Remote"
    HYBRID = "Hybrid"
    ON_SITE = "On-site"


@dataclass(slots=True, kw_only=True)
class Company:
    id: int | None
    name: str
    website: str | None
    industry: str | None

    notes: str | None

    skills: list[Skill] = field(default_factory=list, repr=False)
    contacts: list[Contact] = field(default_factory=list, repr=False)
    applications: list[Application] = field(default_factory=list, repr=False)

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True, kw_only=True)
class Application:
    id: int | None
    company_id: int
    title: str
    description: str | None
    salary_range: str | None
    location_type: Location
    platform: str | None
    url: str | None
    date_applied: datetime | None
    follow_up_date: datetime | None
    notes: str | None

    priority: int = 0
    status: Status = Status.SAVED

    skills: list[Skill] = field(default_factory=list, repr=False)
    contacts: list[Contact] = field(default_factory=list, repr=False)
    history: list[ApplicationHistory] = field(default_factory=list, repr=False)

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        self.validate_priority(self.priority)

    @staticmethod
    def validate_priority(priority: int):
        if priority < 0 or priority > 4:
            raise ValueError("Priority must be between 0 and 4.")


@dataclass(slots=True, kw_only=True, frozen=True)
class ApplicationHistory:
    id: int
    application_id: int
    old_status: Status
    new_status: Status
    changed_at: datetime


@dataclass(slots=True, kw_only=True)
class Skill:
    id: int | None
    name: str

    companies: list[Company] = field(default_factory=list, repr=False)
    applications: list[Application] = field(default_factory=list, repr=False)


@dataclass(slots=True, kw_only=True)
class Contact:
    id: int | None
    name: str
    email: str | None
    phone: str | None
    url: str | None

    notes: str | None

    companies: list[Company] = field(default_factory=list, repr=False)
    applications: list[Application] = field(default_factory=list, repr=False)

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
