from datetime import date, datetime
from enum import StrEnum

from sqlmodel import Field, Relationship, SQLModel, func


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


class CompanySkillLink(SQLModel, table=True):
    company_id: int | None = Field(
        default=None,
        foreign_key="company.id",
        primary_key=True,
    )
    skill_id: int | None = Field(
        default=None,
        foreign_key="skill.id",
        primary_key=True,
    )


class ApplicationSkillLink(SQLModel, table=True):
    application_id: int | None = Field(
        default=None,
        foreign_key="application.id",
        primary_key=True,
    )
    skill_id: int | None = Field(
        default=None,
        foreign_key="skill.id",
        primary_key=True,
    )


class CompanyContactLink(SQLModel, table=True):
    company_id: int | None = Field(
        default=None,
        foreign_key="company.id",
        primary_key=True,
    )
    contact_id: int | None = Field(
        default=None,
        foreign_key="contact.id",
        primary_key=True,
    )


class ApplicationContactLink(SQLModel, table=True):
    application_id: int | None = Field(
        default=None,
        foreign_key="application.id",
        primary_key=True,
    )
    contact_id: int | None = Field(
        default=None,
        foreign_key="contact.id",
        primary_key=True,
    )


class Base(SQLModel):
    id: int | None = Field(default=None, primary_key=True)

    created_at: datetime = Field(default_factory=func.now)
    last_updated: datetime = Field(
        default_factory=func.now,
        sa_column_kwargs={"onupdate": func.now()},
    )


class Company(Base, table=True):
    name: str = Field(index=True, unique=True)
    website: str | None = None
    industry: str | None = None

    notes: str | None = None

    applications: list[Application] = Relationship(
        back_populates="company",
        cascade_delete=True,
    )
    skills: list[Skill] = Relationship(
        back_populates="companies",
        link_model=CompanySkillLink,
    )
    contacts: list[Contact] = Relationship(
        back_populates="companies",
        link_model=CompanyContactLink,
    )


class Application(Base, table=True):
    title: str = Field(index=True)
    description: str | None = None
    salary_range: str | None = None

    platform: str | None = None
    url: str | None = None
    address: str | None = None
    location_type: Location | None = None
    status: Status = Field(default=Status.SAVED, index=True)

    priority: int = Field(default=0, ge=0, le=4)

    date_applied: date | None = None
    follow_up_date: date | None = None

    notes: str | None = None

    company_id: int | None = Field(
        default=None,
        foreign_key="company.id",
        ondelete="CASCADE",
    )
    company: Company | None = Relationship(
        back_populates="applications",
    )
    entries: list[Entry] = Relationship(
        back_populates="application",
        cascade_delete=True,
    )
    skills: list[Skill] = Relationship(
        back_populates="applications",
        link_model=ApplicationSkillLink,
    )
    contacts: list[Contact] = Relationship(
        back_populates="applications",
        link_model=ApplicationContactLink,
    )

    @property
    def company_name(self) -> str:
        return self.company.name


class Entry(Base, table=True):
    content: str

    application_id: int | None = Field(
        default=None,
        foreign_key="application.id",
        ondelete="CASCADE",
    )
    application: Application | None = Relationship(
        back_populates="entries",
    )


class Skill(Base, table=True):
    name: str = Field(index=True, unique=True)

    companies: list[Company] = Relationship(
        back_populates="skills",
        link_model=CompanySkillLink,
    )
    applications: list[Application] = Relationship(
        back_populates="skills",
        link_model=ApplicationSkillLink,
    )


class Contact(Base, table=True):
    name: str = Field(index=True)
    email: str | None = None
    phone: str | None = None
    url: str | None = None

    notes: str | None = None

    companies: list[Company] = Relationship(
        back_populates="contacts",
        link_model=CompanyContactLink,
    )
    applications: list[Application] = Relationship(
        back_populates="contacts",
        link_model=ApplicationContactLink,
    )
