from dataclasses import dataclass, field
from datetime import date
from typing import Any, Self

from jobless.models import Application, Base, Company, Contact, Location, Skill, Status


@dataclass(frozen=True, slots=True, kw_only=True)
class BaseSchema:
    id: int | None = None

    @classmethod
    def from_model(cls, model: Any) -> Self:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        raise NotImplementedError


@dataclass(frozen=True, slots=True, kw_only=True)
class LookupSchema(BaseSchema):
    label: str

    @classmethod
    def from_model(cls, model: Base) -> Self:
        id = getattr(model, "id", None)
        label = getattr(
            model,
            "name",
            getattr(model, "title", str(model)),
        )
        return cls(id=id, label=label)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        label = data.get("name") or data.get("title") or str(data)

        return cls(
            id=data.get("id", None),
            label=label,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class SkillSchema(BaseSchema):
    name: str
    applications: list[LookupSchema] = field(default_factory=list)

    @classmethod
    def from_model(cls, model: Skill) -> Self:
        return cls(
            id=model.id,
            name=model.name,
            applications=[LookupSchema.from_model(app) for app in model.applications],
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        skill_name = data.get("name")
        assert isinstance(skill_name, str)

        return cls(
            id=data.get("id", None),
            name=skill_name,
            applications=data.get("applications", []),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class CompanySchema(BaseSchema):
    name: str
    url: str | None = None
    industry: str | None = None
    notes: str | None = None

    applications: list[LookupSchema] = field(default_factory=list)
    contacts: list[LookupSchema] = field(default_factory=list)

    @classmethod
    def from_model(cls, model: Company) -> Self:
        return cls(
            id=model.id,
            name=model.name,
            url=model.url,
            industry=model.industry,
            notes=model.notes,
            applications=[
                LookupSchema.from_model(application)
                for application in model.applications
            ],
            contacts=[LookupSchema.from_model(contact) for contact in model.contacts],
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        company_name = data.get("name")
        assert isinstance(company_name, str)

        return cls(
            id=data.get("id", None),
            name=company_name,
            url=data.get("url", None),
            industry=data.get("industry", None),
            notes=data.get("notes", None),
            applications=data.get("applications", []),
            contacts=data.get("contacts", []),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class ContactSchema(BaseSchema):
    name: str
    email: str | None = None
    phone: str | None = None
    url: str | None = None
    notes: str | None = None

    companies: list[LookupSchema] = field(default_factory=list)
    applications: list[LookupSchema] = field(default_factory=list)

    @classmethod
    def from_model(cls, model: Contact) -> Self:
        return cls(
            id=model.id,
            name=model.name,
            email=model.email,
            phone=model.phone,
            url=model.url,
            notes=model.notes,
            companies=[LookupSchema.from_model(company) for company in model.companies],
            applications=[
                LookupSchema.from_model(application)
                for application in model.applications
            ],
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        contact_name = data.get("name")
        assert isinstance(contact_name, str)

        return cls(
            id=data.get("id", None),
            name=contact_name,
            email=data.get("email", None),
            phone=data.get("phone", None),
            url=data.get("url", None),
            notes=data.get("notes", None),
            companies=data.get("companies", []),
            applications=data.get("applications", []),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class ApplicationSchema(BaseSchema):
    title: str
    description: str | None = None
    salary_range: str | None = None
    platform: str | None = None
    url: str | None = None
    address: str | None = None
    location_type: Location = Location.ON_SITE
    status: Status = Status.SAVED
    priority: int = field(default=0)
    date_applied: date | None = None
    follow_up_date: date | None = None
    notes: str | None = None
    company: LookupSchema

    contacts: list[LookupSchema] = field(default_factory=list)
    skills: list[LookupSchema] = field(default_factory=list)

    @classmethod
    def from_model(cls, model: Application) -> Self:
        return cls(
            id=model.id,
            title=model.title,
            description=model.description,
            salary_range=model.salary_range,
            platform=model.platform,
            url=model.url,
            address=model.address,
            location_type=model.location_type,
            status=model.status,
            priority=model.priority,
            date_applied=model.date_applied,
            follow_up_date=model.follow_up_date,
            notes=model.notes,
            company=LookupSchema.from_model(model.company),
            contacts=[LookupSchema.from_model(contact) for contact in model.contacts],
            skills=[LookupSchema.from_model(skill) for skill in model.skills],
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        application_title = data.get("title")
        assert isinstance(application_title, str)

        company = data.get("company")
        assert company
        assert company.id

        applied = data.get("date_applied")
        follow_up = data.get("follow_up_date")

        return cls(
            id=data.get("id", None),
            title=application_title,
            description=data.get("description", None),
            salary_range=data.get("salary_range", None),
            platform=data.get("platform", None),
            url=data.get("url", None),
            address=data.get("address", None),
            location_type=data.get("location_type", Location.ON_SITE),
            status=data.get("status", Status.APPLIED),
            priority=data.get("priority", 0),
            date_applied=date.fromisoformat(applied)
            if isinstance(applied, str)
            else applied,
            follow_up_date=date.fromisoformat(follow_up)
            if isinstance(follow_up, str)
            else follow_up,
            notes=data.get("notes", None),
            company=company,
            contacts=data.get("contacts", []),
            skills=data.get("skills", []),
        )
